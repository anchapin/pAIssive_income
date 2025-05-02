"""
ONNX model implementation for the AI Models module.

This module provides specialized classes for working with ONNX models,
including loading, inference, and optimization.
"""

import json
import logging
import os
from typing import Any, Dict, List, Optional, Union

import numpy as np

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Try to import optional dependencies
try:
    import onnxruntime as ort

    ONNX_AVAILABLE = True
except ImportError:
    logger.warning("ONNX Runtime not available. ONNX model support will be limited.")
    ONNX_AVAILABLE = False

try:
    import torch

    TORCH_AVAILABLE = True
except ImportError:
    logger.warning("PyTorch not available. Some ONNX model features will be limited.")
    TORCH_AVAILABLE = False

try:
    from transformers import AutoTokenizer

    TRANSFORMERS_AVAILABLE = True
except ImportError:
    logger.warning(
        "Transformers not available. Text processing for ONNX models will be limited."
    )
    TRANSFORMERS_AVAILABLE = False


class ONNXModel:
    """
    Class for working with ONNX models.
    """

    def __init__(
        self,
        model_path: str,
        model_type: str = "text-generation",
        tokenizer_path: Optional[str] = None,
        device: str = "auto",
        providers: Optional[List[str]] = None,
        optimization_level: int = 99,  # Maximum optimization by default
        **kwargs,
    ):
        """
        Initialize an ONNX model.

        Args:
            model_path: Path to the ONNX model file
            model_type: Type of model (text-generation, image-classification, etc.)
            tokenizer_path: Optional path to the tokenizer (for text models)
            device: Device to run the model on (auto, cpu, cuda, etc.)
            providers: Optional list of execution providers
            optimization_level: Optimization level (0-99)
            **kwargs: Additional parameters for model initialization
        """
        if not ONNX_AVAILABLE:
            raise ImportError(
                "ONNX Runtime not available. Please install it with: pip install onnxruntime"
            )

        self.model_path = model_path
        self.model_type = model_type
        self.tokenizer_path = tokenizer_path
        self.device = device
        self.optimization_level = optimization_level
        self.kwargs = kwargs
        self.session = None
        self.tokenizer = None
        self.metadata = {}
        self.input_names = []
        self.output_names = []

        # Determine providers
        self.providers = providers
        if self.providers is None:
            if self.device == "auto":
                # Auto-detect available providers
                available_providers = ort.get_available_providers()

                # Prioritize GPU providers if available
                if "CUDAExecutionProvider" in available_providers:
                    self.providers = ["CUDAExecutionProvider", "CPUExecutionProvider"]
                elif "TensorrtExecutionProvider" in available_providers:
                    self.providers = [
                        "TensorrtExecutionProvider",
                        "CPUExecutionProvider",
                    ]
                elif "ROCMExecutionProvider" in available_providers:
                    self.providers = ["ROCMExecutionProvider", "CPUExecutionProvider"]
                else:
                    self.providers = ["CPUExecutionProvider"]
            elif self.device == "cpu":
                self.providers = ["CPUExecutionProvider"]
            elif self.device == "cuda":
                self.providers = ["CUDAExecutionProvider", "CPUExecutionProvider"]
            elif self.device == "tensorrt":
                self.providers = ["TensorrtExecutionProvider", "CPUExecutionProvider"]
            elif self.device == "rocm":
                self.providers = ["ROCMExecutionProvider", "CPUExecutionProvider"]
            else:
                # Default to CPU
                self.providers = ["CPUExecutionProvider"]

        logger.info(f"Using ONNX providers: {self.providers}")

    def load(self) -> None:
        """
        Load the ONNX model.
        """
        logger.info(f"Loading ONNX model: {self.model_path}")

        try:
            # Configure session options
            session_options = ort.SessionOptions()
            session_options.graph_optimization_level = self.optimization_level

            # Enable parallel execution
            session_options.enable_cpu_mem_arena = True
            session_options.enable_mem_pattern = True
            session_options.enable_mem_reuse = True

            # Set thread count if specified
            if "num_threads" in self.kwargs:
                session_options.intra_op_num_threads = self.kwargs["num_threads"]
                session_options.inter_op_num_threads = self.kwargs["num_threads"]

            # Create session
            self.session = ort.InferenceSession(
                self.model_path, sess_options=session_options, providers=self.providers
            )

            # Get input and output names
            self.input_names = [input.name for input in self.session.get_inputs()]
            self.output_names = [output.name for output in self.session.get_outputs()]

            # Load metadata if available
            self._load_metadata()

            # Load tokenizer if needed and available
            if (
                self.model_type
                in ["text-generation", "text-classification", "embedding"]
                and TRANSFORMERS_AVAILABLE
            ):
                self._load_tokenizer()

            logger.info(f"Successfully loaded ONNX model: {self.model_path}")
            logger.info(f"Model inputs: {self.input_names}")
            logger.info(f"Model outputs: {self.output_names}")

        except Exception as e:
            logger.error(f"Error loading ONNX model: {e}")
            raise

    def _load_metadata(self) -> None:
        """
        Load metadata from the model.
        """
        try:
            # Try to get metadata from the model
            metadata = self.session.get_modelmeta()
            if metadata and metadata.custom_metadata_map:
                self.metadata = metadata.custom_metadata_map

            # If no metadata in the model, check for a metadata file
            if not self.metadata:
                metadata_path = os.path.splitext(self.model_path)[0] + ".json"
                if os.path.exists(metadata_path):
                    with open(metadata_path, "r") as f:
                        self.metadata = json.load(f)

            if self.metadata:
                logger.info(f"Loaded metadata: {list(self.metadata.keys())}")

        except Exception as e:
            logger.warning(f"Error loading metadata: {e}")

    def _load_tokenizer(self) -> None:
        """
        Load the tokenizer for text models.
        """
        if not TRANSFORMERS_AVAILABLE:
            logger.warning("Transformers not available. Cannot load tokenizer.")
            return

        try:
            # Determine tokenizer path
            tokenizer_path = self.tokenizer_path
            if not tokenizer_path:
                # Check if tokenizer is in the same directory as the model
                model_dir = os.path.dirname(self.model_path)
                if os.path.exists(os.path.join(model_dir, "tokenizer.json")):
                    tokenizer_path = model_dir
                elif "tokenizer" in self.metadata:
                    tokenizer_path = self.metadata["tokenizer"]
                else:
                    # Try to infer from model name
                    model_name = os.path.basename(self.model_path)
                    if "gpt" in model_name.lower():
                        tokenizer_path = "gpt2"
                    elif "bert" in model_name.lower():
                        tokenizer_path = "bert-base-uncased"
                    elif "t5" in model_name.lower():
                        tokenizer_path = "t5-small"
                    else:
                        logger.warning(
                            "Could not determine tokenizer. Please specify tokenizer_path."
                        )
                        return

            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(tokenizer_path)
            logger.info(f"Loaded tokenizer from {tokenizer_path}")

        except Exception as e:
            logger.warning(f"Error loading tokenizer: {e}")

    def generate_text(
        self,
        prompt: str,
        max_length: int = 100,
        temperature: float = 0.7,
        top_p: float = 0.9,
        top_k: int = 50,
        **kwargs,
    ) -> str:
        """
        Generate text using the ONNX model.

        Args:
            prompt: Input prompt
            max_length: Maximum length of generated text
            temperature: Temperature for sampling
            top_p: Top-p sampling parameter
            top_k: Top-k sampling parameter
            **kwargs: Additional parameters for text generation

        Returns:
            Generated text
        """
        if not self.session:
            self.load()

        if not self.tokenizer:
            raise ValueError("Tokenizer not available. Cannot generate text.")

        try:
            # Tokenize input
            inputs = self.tokenizer(prompt, return_tensors="pt")
            input_ids = inputs["input_ids"].numpy()
            attention_mask = inputs["attention_mask"].numpy()

            # Prepare inputs for the model
            onnx_inputs = {}

            # Map inputs based on model's expected input names
            if "input_ids" in self.input_names:
                onnx_inputs["input_ids"] = input_ids

            if "attention_mask" in self.input_names:
                onnx_inputs["attention_mask"] = attention_mask

            # Add generation parameters if the model supports them
            if "max_length" in self.input_names:
                onnx_inputs["max_length"] = np.array([max_length], dtype=np.int64)

            if "temperature" in self.input_names:
                onnx_inputs["temperature"] = np.array([temperature], dtype=np.float32)

            if "top_p" in self.input_names:
                onnx_inputs["top_p"] = np.array([top_p], dtype=np.float32)

            if "top_k" in self.input_names:
                onnx_inputs["top_k"] = np.array([top_k], dtype=np.int64)

            # Run inference
            outputs = self.session.run(self.output_names, onnx_inputs)

            # Process outputs based on model type
            if self.model_type == "text-generation":
                # Get output IDs
                output_ids = outputs[0]

                # Decode output
                if output_ids.ndim > 1:
                    output_text = self.tokenizer.decode(
                        output_ids[0], skip_special_tokens=True
                    )
                else:
                    output_text = self.tokenizer.decode(
                        output_ids, skip_special_tokens=True
                    )

                return output_text

            else:
                # For other model types, return raw outputs
                return str(outputs)

        except Exception as e:
            logger.error(f"Error generating text: {e}")
            raise

    def classify_text(self, text: str, **kwargs) -> Dict[str, float]:
        """
        Classify text using the ONNX model.

        Args:
            text: Input text
            **kwargs: Additional parameters for classification

        Returns:
            Dictionary of class labels and scores
        """
        if not self.session:
            self.load()

        if not self.tokenizer:
            raise ValueError("Tokenizer not available. Cannot classify text.")

        try:
            # Tokenize input
            inputs = self.tokenizer(text, return_tensors="pt")
            input_ids = inputs["input_ids"].numpy()
            attention_mask = inputs["attention_mask"].numpy()

            # Prepare inputs for the model
            onnx_inputs = {}

            # Map inputs based on model's expected input names
            if "input_ids" in self.input_names:
                onnx_inputs["input_ids"] = input_ids

            if "attention_mask" in self.input_names:
                onnx_inputs["attention_mask"] = attention_mask

            # Run inference
            outputs = self.session.run(self.output_names, onnx_inputs)

            # Process outputs
            logits = outputs[0]

            # Convert logits to probabilities
            if TORCH_AVAILABLE:
                probs = torch.nn.functional.softmax(
                    torch.tensor(logits), dim=-1
                ).numpy()
            else:
                # Manual softmax
                exp_logits = np.exp(logits - np.max(logits, axis=-1, keepdims=True))
                probs = exp_logits / np.sum(exp_logits, axis=-1, keepdims=True)

            # Get class labels if available
            labels = []
            if "id2label" in self.metadata:
                id2label = json.loads(self.metadata["id2label"])
                labels = [
                    id2label.get(str(i), f"Class {i}") for i in range(probs.shape[-1])
                ]
            else:
                labels = [f"Class {i}" for i in range(probs.shape[-1])]

            # Create result dictionary
            result = {label: float(prob) for label, prob in zip(labels, probs[0])}

            return result

        except Exception as e:
            logger.error(f"Error classifying text: {e}")
            raise

    def encode(self, texts: Union[str, List[str]], **kwargs) -> np.ndarray:
        """
        Generate embeddings for text using the ONNX model.

        Args:
            texts: Input text or list of texts
            **kwargs: Additional parameters for encoding

        Returns:
            Numpy array of embeddings
        """
        if not self.session:
            self.load()

        if not self.tokenizer:
            raise ValueError("Tokenizer not available. Cannot encode text.")

        try:
            # Handle single text or list of texts
            if isinstance(texts, str):
                texts = [texts]

            # Tokenize input
            inputs = self.tokenizer(
                texts, padding=True, truncation=True, return_tensors="pt"
            )

            input_ids = inputs["input_ids"].numpy()
            attention_mask = inputs["attention_mask"].numpy()

            # Prepare inputs for the model
            onnx_inputs = {}

            # Map inputs based on model's expected input names
            if "input_ids" in self.input_names:
                onnx_inputs["input_ids"] = input_ids

            if "attention_mask" in self.input_names:
                onnx_inputs["attention_mask"] = attention_mask

            # Run inference
            outputs = self.session.run(self.output_names, onnx_inputs)

            # Process outputs
            embeddings = outputs[0]

            # Normalize embeddings if requested
            if kwargs.get("normalize", True):
                if TORCH_AVAILABLE:
                    embeddings = torch.nn.functional.normalize(
                        torch.tensor(embeddings), p=2, dim=1
                    ).numpy()
                else:
                    # Manual normalization
                    norms = np.sqrt(np.sum(embeddings**2, axis=1, keepdims=True))
                    embeddings = embeddings / norms

            return embeddings

        except Exception as e:
            logger.error(f"Error encoding text: {e}")
            raise

    def classify_image(self, image_path: str, **kwargs) -> Dict[str, float]:
        """
        Classify an image using the ONNX model.

        Args:
            image_path: Path to the image file
            **kwargs: Additional parameters for classification

        Returns:
            Dictionary of class labels and scores
        """
        if not self.session:
            self.load()

        try:
            # Load and preprocess image
            image_data = self._preprocess_image(image_path)

            # Prepare inputs for the model
            onnx_inputs = {}

            # Map inputs based on model's expected input names
            if len(self.input_names) == 1:
                # If there's only one input, use it directly
                onnx_inputs[self.input_names[0]] = image_data
            else:
                # Try to map to common input names
                if "input" in self.input_names:
                    onnx_inputs["input"] = image_data
                elif "images" in self.input_names:
                    onnx_inputs["images"] = image_data
                elif "pixel_values" in self.input_names:
                    onnx_inputs["pixel_values"] = image_data
                else:
                    # Use the first input name
                    onnx_inputs[self.input_names[0]] = image_data

            # Run inference
            outputs = self.session.run(self.output_names, onnx_inputs)

            # Process outputs
            logits = outputs[0]

            # Convert logits to probabilities
            if TORCH_AVAILABLE:
                probs = torch.nn.functional.softmax(
                    torch.tensor(logits), dim=-1
                ).numpy()
            else:
                # Manual softmax
                exp_logits = np.exp(logits - np.max(logits, axis=-1, keepdims=True))
                probs = exp_logits / np.sum(exp_logits, axis=-1, keepdims=True)

            # Get class labels if available
            labels = []
            if "id2label" in self.metadata:
                id2label = json.loads(self.metadata["id2label"])
                labels = [
                    id2label.get(str(i), f"Class {i}") for i in range(probs.shape[-1])
                ]
            else:
                # Try to load ImageNet labels if it's a common image classification model
                try:
                    from torchvision.models import list_models

                    labels = list_models()
                except Exception:
                    labels = [f"Class {i}" for i in range(probs.shape[-1])]

            # Create result dictionary
            result = {label: float(prob) for label, prob in zip(labels, probs[0])}

            return result

        except Exception as e:
            logger.error(f"Error classifying image: {e}")
            raise

    def _preprocess_image(self, image_path: str) -> np.ndarray:
        """
        Preprocess an image for the model.

        Args:
            image_path: Path to the image file

        Returns:
            Preprocessed image as numpy array
        """
        try:
            # Try to use PIL for image loading
            from PIL import Image

            # Load image
            image = Image.open(image_path).convert("RGB")

            # Resize image
            input_shape = self.session.get_inputs()[0].shape
            if len(input_shape) == 4:
                # NCHW format
                height, width = input_shape[2], input_shape[3]
            else:
                # Default to 224x224
                height, width = 224, 224

            image = image.resize((width, height))

            # Convert to numpy array
            image_data = np.array(image).astype(np.float32)

            # Normalize
            image_data = image_data / 255.0
            mean = np.array([0.485, 0.456, 0.406]).reshape(1, 1, 3)
            std = np.array([0.229, 0.224, 0.225]).reshape(1, 1, 3)
            image_data = (image_data - mean) / std

            # Transpose from HWC to CHW
            image_data = image_data.transpose(2, 0, 1)

            # Add batch dimension
            image_data = np.expand_dims(image_data, axis=0)

            return image_data

        except Exception as e:
            logger.error(f"Error preprocessing image: {e}")
            raise

    def get_metadata(self) -> Dict[str, Any]:
        """
        Get metadata about the model.

        Returns:
            Dictionary with model metadata
        """
        if not self.session:
            self.load()

        metadata = {
            "model_path": self.model_path,
            "model_type": self.model_type,
            "providers": self.providers,
            "input_names": self.input_names,
            "output_names": self.output_names,
            "custom_metadata": self.metadata,
        }

        # Add model metadata
        model_meta = self.session.get_modelmeta()
        if model_meta:
            metadata["description"] = model_meta.description
            metadata["domain"] = model_meta.domain
            metadata["graph_name"] = model_meta.graph_name
            metadata["producer_name"] = model_meta.producer_name
            metadata["version"] = model_meta.version

        return metadata


# Example usage
if __name__ == "__main__":
    # Check if ONNX Runtime is available
    if not ONNX_AVAILABLE:
        print(
            "ONNX Runtime not available. Please install it with: pip install onnxruntime"
        )
        exit(1)

    # Example model path (replace with an actual ONNX model path)
    model_path = "path/to/model.onnx"

    if os.path.exists(model_path):
        # Create ONNX model
        model = ONNXModel(model_path=model_path, model_type="text-generation")

        # Load the model
        model.load()

        # Get metadata
        metadata = model.get_metadata()
        print("Model Metadata:")
        for key, value in metadata.items():
            print(f"  {key}: {value}")

        # Generate text
        if model.tokenizer:
            prompt = "Hello, world!"
            print(f"\nGenerating text for prompt: {prompt}")
            output = model.generate_text(prompt)
            print(f"Output: {output}")
    else:
        print(f"Model file not found: {model_path}")
        print("Please specify a valid ONNX model path.")
