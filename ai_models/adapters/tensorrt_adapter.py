"""
TensorRT adapter for the AI Models module.

This module provides an adapter for using TensorRT for GPU-accelerated inference.
"""

import os
import logging
import numpy as np
from typing import Dict, List, Any, Optional, Union, Tuple

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
        "PyTorch not available. TensorRT adapter will have limited functionality."
    )
    TORCH_AVAILABLE = False

try:
    import tensorrt as trt

    TENSORRT_AVAILABLE = True
except ImportError:
    logger.warning(
        "TensorRT not available. Please install it to use the TensorRT adapter."
    )
    TENSORRT_AVAILABLE = False

try:
    import pycuda.driver as cuda
    import pycuda.autoinit

    PYCUDA_AVAILABLE = True
except ImportError:
    logger.warning(
        "PyCUDA not available. Please install it to use the TensorRT adapter."
    )
    PYCUDA_AVAILABLE = False

try:
    from transformers import AutoTokenizer

    TRANSFORMERS_AVAILABLE = True
except ImportError:
    logger.warning("Transformers not available. Text processing will be limited.")
    TRANSFORMERS_AVAILABLE = False


class TensorRTAdapter:
    """
    Adapter for using TensorRT for GPU-accelerated inference.
    """

    def __init__(
        self,
        engine_path: str,
        model_type: str = "text-generation",
        tokenizer_path: Optional[str] = None,
        max_batch_size: int = 1,
        **kwargs,
    ):
        """
        Initialize the TensorRT adapter.

        Args:
            engine_path: Path to the TensorRT engine file
            model_type: Type of model (text-generation, image-classification, etc.)
            tokenizer_path: Optional path to the tokenizer (for text models)
            max_batch_size: Maximum batch size for inference
            **kwargs: Additional parameters for the adapter
        """
        if not TENSORRT_AVAILABLE:
            raise ImportError(
                "TensorRT not available. Please install it to use the TensorRT adapter."
            )

        if not PYCUDA_AVAILABLE:
            raise ImportError(
                "PyCUDA not available. Please install it to use the TensorRT adapter."
            )

        self.engine_path = engine_path
        self.model_type = model_type
        self.tokenizer_path = tokenizer_path
        self.max_batch_size = max_batch_size
        self.kwargs = kwargs

        self.engine = None
        self.context = None
        self.tokenizer = None
        self.input_names = []
        self.output_names = []
        self.bindings = []
        self.binding_shapes = {}
        self.binding_dtypes = {}
        self.stream = None

        # Load the engine
        self._load_engine()

        # Load the tokenizer if needed
        if (
            self.model_type in ["text-generation", "text-classification", "embedding"]
            and self.tokenizer_path
        ):
            self._load_tokenizer()

    def _load_engine(self) -> None:
        """
        Load the TensorRT engine.
        """
        logger.info(f"Loading TensorRT engine: {self.engine_path}")

        try:
            # Initialize TensorRT
            logger.info("Initializing TensorRT")
            trt_logger = trt.Logger(trt.Logger.WARNING)
            runtime = trt.Runtime(trt_logger)

            # Load the engine
            with open(self.engine_path, "rb") as f:
                engine_data = f.read()

            self.engine = runtime.deserialize_cuda_engine(engine_data)

            if not self.engine:
                raise ValueError(
                    f"Failed to load TensorRT engine from {self.engine_path}"
                )

            # Create execution context
            self.context = self.engine.create_execution_context()

            # Get input and output names
            for i in range(self.engine.num_bindings):
                name = self.engine.get_binding_name(i)
                shape = self.engine.get_binding_shape(i)
                dtype = trt.nptype(self.engine.get_binding_dtype(i))

                if self.engine.binding_is_input(i):
                    self.input_names.append(name)
                else:
                    self.output_names.append(name)

                self.binding_shapes[name] = shape
                self.binding_dtypes[name] = dtype

            # Create CUDA stream
            self.stream = cuda.Stream()

            logger.info(f"Successfully loaded TensorRT engine: {self.engine_path}")
            logger.info(f"Input names: {self.input_names}")
            logger.info(f"Output names: {self.output_names}")

        except Exception as e:
            logger.error(f"Error loading TensorRT engine: {e}")
            raise

    def _load_tokenizer(self) -> None:
        """
        Load the tokenizer for text models.
        """
        if not TRANSFORMERS_AVAILABLE:
            logger.warning("Transformers not available. Cannot load tokenizer.")
            return

        try:
            logger.info(f"Loading tokenizer from {self.tokenizer_path}")
            self.tokenizer = AutoTokenizer.from_pretrained(self.tokenizer_path)
            logger.info("Tokenizer loaded successfully")

        except Exception as e:
            logger.error(f"Error loading tokenizer: {e}")
            raise

    def _allocate_buffers(
        self, input_shapes: Dict[str, Tuple]
    ) -> Tuple[List, List, List]:
        """
        Allocate device buffers for inputs and outputs.

        Args:
            input_shapes: Dictionary of input names and shapes

        Returns:
            Tuple of (host_buffers, device_buffers, bindings)
        """
        host_buffers = []
        device_buffers = []
        bindings = []

        # Set dynamic shapes for inputs
        for name, shape in input_shapes.items():
            if name in self.input_names:
                index = self.engine.get_binding_index(name)
                self.context.set_binding_shape(index, shape)

        # Allocate buffers for all bindings
        for i in range(self.engine.num_bindings):
            name = self.engine.get_binding_name(i)
            shape = self.context.get_binding_shape(i)
            dtype = self.binding_dtypes[name]

            # Calculate size
            size = trt.volume(shape) * np.dtype(dtype).itemsize

            # Allocate host and device buffers
            host_buffer = cuda.pagelocked_empty(trt.volume(shape), dtype)
            device_buffer = cuda.mem_alloc(size)

            host_buffers.append(host_buffer)
            device_buffers.append(device_buffer)
            bindings.append(int(device_buffer))

        return host_buffers, device_buffers, bindings

    def _infer(self, inputs: Dict[str, np.ndarray]) -> Dict[str, np.ndarray]:
        """
        Run inference with the TensorRT engine.

        Args:
            inputs: Dictionary of input names and numpy arrays

        Returns:
            Dictionary of output names and numpy arrays
        """
        # Prepare input shapes
        input_shapes = {}
        for name, array in inputs.items():
            input_shapes[name] = array.shape

        # Allocate buffers
        host_buffers, device_buffers, bindings = self._allocate_buffers(input_shapes)

        # Copy inputs to host buffers
        for name, array in inputs.items():
            index = self.engine.get_binding_index(name)
            host_buffers[index] = np.ascontiguousarray(array)
            cuda.memcpy_htod_async(
                device_buffers[index], host_buffers[index], self.stream
            )

        # Run inference
        self.context.execute_async_v2(
            bindings=bindings, stream_handle=self.stream.handle
        )

        # Copy outputs from device to host
        outputs = {}
        for i, name in enumerate(self.output_names):
            index = self.engine.get_binding_index(name)
            cuda.memcpy_dtoh_async(
                host_buffers[index], device_buffers[index], self.stream
            )

        # Synchronize
        self.stream.synchronize()

        # Get outputs
        for name in self.output_names:
            index = self.engine.get_binding_index(name)
            shape = self.context.get_binding_shape(index)
            outputs[name] = host_buffers[index].reshape(shape)

        return outputs

    def generate_text(
        self,
        prompt: str,
        max_tokens: int = 100,
        temperature: float = 0.7,
        top_p: float = 0.9,
        top_k: int = 40,
        **kwargs,
    ) -> str:
        """
        Generate text using the TensorRT engine.

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
        if self.model_type != "text-generation":
            raise ValueError(
                f"Model type {self.model_type} does not support text generation"
            )

        if not self.tokenizer:
            raise ValueError("Tokenizer not available. Cannot generate text.")

        try:
            # Tokenize input
            inputs = self.tokenizer(prompt, return_tensors="np")

            # Prepare inputs for the model
            model_inputs = {}

            # Map inputs based on model's expected input names
            for name in self.input_names:
                if name == "input_ids" and "input_ids" in inputs:
                    model_inputs[name] = inputs["input_ids"]
                elif name == "attention_mask" and "attention_mask" in inputs:
                    model_inputs[name] = inputs["attention_mask"]
                elif name == "max_length":
                    model_inputs[name] = np.array(
                        [len(inputs["input_ids"][0]) + max_tokens], dtype=np.int32
                    )
                elif name == "temperature":
                    model_inputs[name] = np.array([temperature], dtype=np.float32)
                elif name == "top_p":
                    model_inputs[name] = np.array([top_p], dtype=np.float32)
                elif name == "top_k":
                    model_inputs[name] = np.array([top_k], dtype=np.int32)

            # Run inference
            outputs = self._infer(model_inputs)

            # Process outputs
            if "output_ids" in outputs:
                output_ids = outputs["output_ids"]

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
                # Try to find output tensor
                for name, tensor in outputs.items():
                    if "output" in name.lower() or "ids" in name.lower():
                        # Decode output
                        if tensor.ndim > 1:
                            output_text = self.tokenizer.decode(
                                tensor[0], skip_special_tokens=True
                            )
                        else:
                            output_text = self.tokenizer.decode(
                                tensor, skip_special_tokens=True
                            )

                        return output_text

            # If no output found
            raise ValueError("Could not find output tensor in model outputs")

        except Exception as e:
            logger.error(f"Error generating text: {e}")
            raise

    def classify_text(self, text: str, **kwargs) -> Dict[str, float]:
        """
        Classify text using the TensorRT engine.

        Args:
            text: Input text
            **kwargs: Additional parameters for classification

        Returns:
            Dictionary of class labels and scores
        """
        if self.model_type != "text-classification":
            raise ValueError(
                f"Model type {self.model_type} does not support text classification"
            )

        if not self.tokenizer:
            raise ValueError("Tokenizer not available. Cannot classify text.")

        try:
            # Tokenize input
            inputs = self.tokenizer(text, return_tensors="np")

            # Prepare inputs for the model
            model_inputs = {}

            # Map inputs based on model's expected input names
            for name in self.input_names:
                if name == "input_ids" and "input_ids" in inputs:
                    model_inputs[name] = inputs["input_ids"]
                elif name == "attention_mask" and "attention_mask" in inputs:
                    model_inputs[name] = inputs["attention_mask"]

            # Run inference
            outputs = self._infer(model_inputs)

            # Process outputs
            if "logits" in outputs:
                logits = outputs["logits"]
            else:
                # Try to find output tensor
                for name, tensor in outputs.items():
                    if "logits" in name.lower() or "output" in name.lower():
                        logits = tensor
                        break
                else:
                    raise ValueError("Could not find logits tensor in model outputs")

            # Convert logits to probabilities
            if TORCH_AVAILABLE:
                logits_tensor = torch.from_numpy(logits)
                probs = torch.nn.functional.softmax(logits_tensor, dim=-1).numpy()
            else:
                # Manual softmax
                exp_logits = np.exp(logits - np.max(logits, axis=-1, keepdims=True))
                probs = exp_logits / np.sum(exp_logits, axis=-1, keepdims=True)

            # Get class labels
            labels = []
            if hasattr(self.tokenizer, "id2label"):
                labels = [self.tokenizer.id2label[i] for i in range(probs.shape[-1])]
            else:
                labels = [f"Class {i}" for i in range(probs.shape[-1])]

            # Create result dictionary
            result = {label: float(prob) for label, prob in zip(labels, probs[0])}

            return result

        except Exception as e:
            logger.error(f"Error classifying text: {e}")
            raise

    def create_embedding(self, text: Union[str, List[str]], **kwargs) -> np.ndarray:
        """
        Create embeddings for text using the TensorRT engine.

        Args:
            text: Input text or list of texts
            **kwargs: Additional parameters for embedding

        Returns:
            Numpy array of embeddings
        """
        if self.model_type != "embedding":
            raise ValueError(f"Model type {self.model_type} does not support embedding")

        if not self.tokenizer:
            raise ValueError("Tokenizer not available. Cannot create embeddings.")

        try:
            # Handle single text or list of texts
            if isinstance(text, str):
                texts = [text]
            else:
                texts = text

            # Tokenize input
            inputs = self.tokenizer(
                texts, padding=True, truncation=True, return_tensors="np"
            )

            # Prepare inputs for the model
            model_inputs = {}

            # Map inputs based on model's expected input names
            for name in self.input_names:
                if name == "input_ids" and "input_ids" in inputs:
                    model_inputs[name] = inputs["input_ids"]
                elif name == "attention_mask" and "attention_mask" in inputs:
                    model_inputs[name] = inputs["attention_mask"]

            # Run inference
            outputs = self._infer(model_inputs)

            # Process outputs
            if "embeddings" in outputs:
                embeddings = outputs["embeddings"]
            else:
                # Try to find output tensor
                for name, tensor in outputs.items():
                    if "embedding" in name.lower() or "output" in name.lower():
                        embeddings = tensor
                        break
                else:
                    raise ValueError(
                        "Could not find embeddings tensor in model outputs"
                    )

            # Normalize embeddings if requested
            if kwargs.get("normalize", True):
                if TORCH_AVAILABLE:
                    embeddings_tensor = torch.from_numpy(embeddings)
                    embeddings = torch.nn.functional.normalize(
                        embeddings_tensor, p=2, dim=1
                    ).numpy()
                else:
                    # Manual normalization
                    norms = np.sqrt(np.sum(embeddings**2, axis=1, keepdims=True))
                    embeddings = embeddings / norms

            return embeddings

        except Exception as e:
            logger.error(f"Error creating embeddings: {e}")
            raise

    def classify_image(self, image_path: str, **kwargs) -> Dict[str, float]:
        """
        Classify an image using the TensorRT engine.

        Args:
            image_path: Path to the image file
            **kwargs: Additional parameters for classification

        Returns:
            Dictionary of class labels and scores
        """
        if self.model_type != "image-classification":
            raise ValueError(
                f"Model type {self.model_type} does not support image classification"
            )

        try:
            # Load and preprocess image
            image_data = self._preprocess_image(image_path)

            # Prepare inputs for the model
            model_inputs = {}

            # Map inputs based on model's expected input names
            if len(self.input_names) == 1:
                # If there's only one input, use it directly
                model_inputs[self.input_names[0]] = image_data
            else:
                # Try to map to common input names
                for name in self.input_names:
                    if name in ["input", "images", "pixel_values"]:
                        model_inputs[name] = image_data
                        break
                else:
                    # Use the first input name
                    model_inputs[self.input_names[0]] = image_data

            # Run inference
            outputs = self._infer(model_inputs)

            # Process outputs
            if "logits" in outputs:
                logits = outputs["logits"]
            else:
                # Try to find output tensor
                for name, tensor in outputs.items():
                    if "logits" in name.lower() or "output" in name.lower():
                        logits = tensor
                        break
                else:
                    raise ValueError("Could not find logits tensor in model outputs")

            # Convert logits to probabilities
            if TORCH_AVAILABLE:
                logits_tensor = torch.from_numpy(logits)
                probs = torch.nn.functional.softmax(logits_tensor, dim=-1).numpy()
            else:
                # Manual softmax
                exp_logits = np.exp(logits - np.max(logits, axis=-1, keepdims=True))
                probs = exp_logits / np.sum(exp_logits, axis=-1, keepdims=True)

            # Get class labels
            labels = kwargs.get(
                "labels", [f"Class {i}" for i in range(probs.shape[-1])]
            )

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
            from PIL import Image

            # Load image
            image = Image.open(image_path).convert("RGB")

            # Resize image
            input_shape = self.binding_shapes[self.input_names[0]]
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
        Get metadata about the TensorRT engine.

        Returns:
            Dictionary with engine metadata
        """
        metadata = {
            "engine_path": self.engine_path,
            "model_type": self.model_type,
            "max_batch_size": self.max_batch_size,
            "input_names": self.input_names,
            "output_names": self.output_names,
            "binding_shapes": {
                name: list(shape) for name, shape in self.binding_shapes.items()
            },
            "binding_dtypes": {
                name: str(dtype) for name, dtype in self.binding_dtypes.items()
            },
        }

        return metadata


# Example usage
if __name__ == "__main__":
    # Check if TensorRT is available
    if not TENSORRT_AVAILABLE or not PYCUDA_AVAILABLE:
        print(
            "TensorRT or PyCUDA not available. Please install them to use the TensorRT adapter."
        )
        exit(1)

    # Example engine path (replace with an actual TensorRT engine path)
    engine_path = "path/to/engine.trt"

    if os.path.exists(engine_path):
        # Create TensorRT adapter
        adapter = TensorRTAdapter(
            engine_path=engine_path,
            model_type="text-generation",
            tokenizer_path="path/to/tokenizer",
        )

        # Get metadata
        metadata = adapter.get_metadata()
        print("Engine Metadata:")
        for key, value in metadata.items():
            print(f"  {key}: {value}")

        # Generate text
        if adapter.tokenizer:
            prompt = "Hello, world!"
            print(f"\nGenerating text for prompt: {prompt}")
            output = adapter.generate_text(prompt)
            print(f"Output: {output}")
    else:
        print(f"Engine file not found: {engine_path}")
        print("Please specify a valid TensorRT engine path.")
