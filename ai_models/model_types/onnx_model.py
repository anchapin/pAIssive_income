"""
"""
ONNX model implementation for the AI Models module.
ONNX model implementation for the AI Models module.


This module provides specialized classes for working with ONNX models,
This module provides specialized classes for working with ONNX models,
including loading, inference, and optimization.
including loading, inference, and optimization.
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




    import json
    import json
    import logging
    import logging
    import os
    import os
    from typing import Any, Dict, List, Optional, Union
    from typing import Any, Dict, List, Optional, Union


    import numpy as np
    import numpy as np
    import onnxruntime
    import onnxruntime
    import torch
    import torch
    from transformers import AutoTokenizer
    from transformers import AutoTokenizer


    TRANSFORMERS_AVAILABLE
    TRANSFORMERS_AVAILABLE
    from torchvision.models import list_models
    from torchvision.models import list_models


    labels
    labels
    from PIL import Image
    from PIL import Image






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
    as ort
    as ort


    ONNX_AVAILABLE = True
    ONNX_AVAILABLE = True
except ImportError:
except ImportError:
    logger.warning("ONNX Runtime not available. ONNX model support will be limited.")
    logger.warning("ONNX Runtime not available. ONNX model support will be limited.")
    ONNX_AVAILABLE = False
    ONNX_AVAILABLE = False


    try:
    try:




    TORCH_AVAILABLE = True
    TORCH_AVAILABLE = True
except ImportError:
except ImportError:
    logger.warning("PyTorch not available. Some ONNX model features will be limited.")
    logger.warning("PyTorch not available. Some ONNX model features will be limited.")
    TORCH_AVAILABLE = False
    TORCH_AVAILABLE = False


    try:
    try:
    = True
    = True
except ImportError:
except ImportError:
    logger.warning(
    logger.warning(
    "Transformers not available. Text processing for ONNX models will be limited."
    "Transformers not available. Text processing for ONNX models will be limited."
    )
    )
    TRANSFORMERS_AVAILABLE = False
    TRANSFORMERS_AVAILABLE = False




    class ONNXModel:
    class ONNXModel:
    """
    """
    Class for working with ONNX models.
    Class for working with ONNX models.
    """
    """


    def __init__(
    def __init__(
    self,
    self,
    model_path: str,
    model_path: str,
    model_type: str = "text-generation",
    model_type: str = "text-generation",
    tokenizer_path: Optional[str] = None,
    tokenizer_path: Optional[str] = None,
    device: str = "auto",
    device: str = "auto",
    providers: Optional[List[str]] = None,
    providers: Optional[List[str]] = None,
    optimization_level: int = 99,  # Maximum optimization by default
    optimization_level: int = 99,  # Maximum optimization by default
    **kwargs,
    **kwargs,
    ):
    ):
    """
    """
    Initialize an ONNX model.
    Initialize an ONNX model.


    Args:
    Args:
    model_path: Path to the ONNX model file
    model_path: Path to the ONNX model file
    model_type: Type of model (text-generation, image-classification, etc.)
    model_type: Type of model (text-generation, image-classification, etc.)
    tokenizer_path: Optional path to the tokenizer (for text models)
    tokenizer_path: Optional path to the tokenizer (for text models)
    device: Device to run the model on (auto, cpu, cuda, etc.)
    device: Device to run the model on (auto, cpu, cuda, etc.)
    providers: Optional list of execution providers
    providers: Optional list of execution providers
    optimization_level: Optimization level (0-99)
    optimization_level: Optimization level (0-99)
    **kwargs: Additional parameters for model initialization
    **kwargs: Additional parameters for model initialization
    """
    """
    if not ONNX_AVAILABLE:
    if not ONNX_AVAILABLE:
    raise ImportError(
    raise ImportError(
    "ONNX Runtime not available. Please install it with: pip install onnxruntime"
    "ONNX Runtime not available. Please install it with: pip install onnxruntime"
    )
    )


    self.model_path = model_path
    self.model_path = model_path
    self.model_type = model_type
    self.model_type = model_type
    self.tokenizer_path = tokenizer_path
    self.tokenizer_path = tokenizer_path
    self.device = device
    self.device = device
    self.optimization_level = optimization_level
    self.optimization_level = optimization_level
    self.kwargs = kwargs
    self.kwargs = kwargs
    self.session = None
    self.session = None
    self.tokenizer = None
    self.tokenizer = None
    self.metadata = {}
    self.metadata = {}
    self.input_names = []
    self.input_names = []
    self.output_names = []
    self.output_names = []


    # Determine providers
    # Determine providers
    self.providers = providers
    self.providers = providers
    if self.providers is None:
    if self.providers is None:
    if self.device == "auto":
    if self.device == "auto":
    # Auto-detect available providers
    # Auto-detect available providers
    available_providers = ort.get_available_providers()
    available_providers = ort.get_available_providers()


    # Prioritize GPU providers if available
    # Prioritize GPU providers if available
    if "CUDAExecutionProvider" in available_providers:
    if "CUDAExecutionProvider" in available_providers:
    self.providers = ["CUDAExecutionProvider", "CPUExecutionProvider"]
    self.providers = ["CUDAExecutionProvider", "CPUExecutionProvider"]
    elif "TensorrtExecutionProvider" in available_providers:
    elif "TensorrtExecutionProvider" in available_providers:
    self.providers = [
    self.providers = [
    "TensorrtExecutionProvider",
    "TensorrtExecutionProvider",
    "CPUExecutionProvider",
    "CPUExecutionProvider",
    ]
    ]
    elif "ROCMExecutionProvider" in available_providers:
    elif "ROCMExecutionProvider" in available_providers:
    self.providers = ["ROCMExecutionProvider", "CPUExecutionProvider"]
    self.providers = ["ROCMExecutionProvider", "CPUExecutionProvider"]
    else:
    else:
    self.providers = ["CPUExecutionProvider"]
    self.providers = ["CPUExecutionProvider"]
    elif self.device == "cpu":
    elif self.device == "cpu":
    self.providers = ["CPUExecutionProvider"]
    self.providers = ["CPUExecutionProvider"]
    elif self.device == "cuda":
    elif self.device == "cuda":
    self.providers = ["CUDAExecutionProvider", "CPUExecutionProvider"]
    self.providers = ["CUDAExecutionProvider", "CPUExecutionProvider"]
    elif self.device == "tensorrt":
    elif self.device == "tensorrt":
    self.providers = ["TensorrtExecutionProvider", "CPUExecutionProvider"]
    self.providers = ["TensorrtExecutionProvider", "CPUExecutionProvider"]
    elif self.device == "rocm":
    elif self.device == "rocm":
    self.providers = ["ROCMExecutionProvider", "CPUExecutionProvider"]
    self.providers = ["ROCMExecutionProvider", "CPUExecutionProvider"]
    else:
    else:
    # Default to CPU
    # Default to CPU
    self.providers = ["CPUExecutionProvider"]
    self.providers = ["CPUExecutionProvider"]


    logger.info(f"Using ONNX providers: {self.providers}")
    logger.info(f"Using ONNX providers: {self.providers}")


    def load(self) -> None:
    def load(self) -> None:
    """
    """
    Load the ONNX model.
    Load the ONNX model.
    """
    """
    logger.info(f"Loading ONNX model: {self.model_path}")
    logger.info(f"Loading ONNX model: {self.model_path}")


    try:
    try:
    # Configure session options
    # Configure session options
    session_options = ort.SessionOptions()
    session_options = ort.SessionOptions()
    session_options.graph_optimization_level = self.optimization_level
    session_options.graph_optimization_level = self.optimization_level


    # Enable parallel execution
    # Enable parallel execution
    session_options.enable_cpu_mem_arena = True
    session_options.enable_cpu_mem_arena = True
    session_options.enable_mem_pattern = True
    session_options.enable_mem_pattern = True
    session_options.enable_mem_reuse = True
    session_options.enable_mem_reuse = True


    # Set thread count if specified
    # Set thread count if specified
    if "num_threads" in self.kwargs:
    if "num_threads" in self.kwargs:
    session_options.intra_op_num_threads = self.kwargs["num_threads"]
    session_options.intra_op_num_threads = self.kwargs["num_threads"]
    session_options.inter_op_num_threads = self.kwargs["num_threads"]
    session_options.inter_op_num_threads = self.kwargs["num_threads"]


    # Create session
    # Create session
    self.session = ort.InferenceSession(
    self.session = ort.InferenceSession(
    self.model_path, sess_options=session_options, providers=self.providers
    self.model_path, sess_options=session_options, providers=self.providers
    )
    )


    # Get input and output names
    # Get input and output names
    self.input_names = [input.name for input in self.session.get_inputs()]
    self.input_names = [input.name for input in self.session.get_inputs()]
    self.output_names = [output.name for output in self.session.get_outputs()]
    self.output_names = [output.name for output in self.session.get_outputs()]


    # Load metadata if available
    # Load metadata if available
    self._load_metadata()
    self._load_metadata()


    # Load tokenizer if needed and available
    # Load tokenizer if needed and available
    if (
    if (
    self.model_type
    self.model_type
    in ["text-generation", "text-classification", "embedding"]
    in ["text-generation", "text-classification", "embedding"]
    and TRANSFORMERS_AVAILABLE
    and TRANSFORMERS_AVAILABLE
    ):
    ):
    self._load_tokenizer()
    self._load_tokenizer()


    logger.info(f"Successfully loaded ONNX model: {self.model_path}")
    logger.info(f"Successfully loaded ONNX model: {self.model_path}")
    logger.info(f"Model inputs: {self.input_names}")
    logger.info(f"Model inputs: {self.input_names}")
    logger.info(f"Model outputs: {self.output_names}")
    logger.info(f"Model outputs: {self.output_names}")


except Exception as e:
except Exception as e:
    logger.error(f"Error loading ONNX model: {e}")
    logger.error(f"Error loading ONNX model: {e}")
    raise
    raise


    def _load_metadata(self) -> None:
    def _load_metadata(self) -> None:
    """
    """
    Load metadata from the model.
    Load metadata from the model.
    """
    """
    try:
    try:
    # Try to get metadata from the model
    # Try to get metadata from the model
    metadata = self.session.get_modelmeta()
    metadata = self.session.get_modelmeta()
    if metadata and metadata.custom_metadata_map:
    if metadata and metadata.custom_metadata_map:
    self.metadata = metadata.custom_metadata_map
    self.metadata = metadata.custom_metadata_map


    # If no metadata in the model, check for a metadata file
    # If no metadata in the model, check for a metadata file
    if not self.metadata:
    if not self.metadata:
    metadata_path = os.path.splitext(self.model_path)[0] + ".json"
    metadata_path = os.path.splitext(self.model_path)[0] + ".json"
    if os.path.exists(metadata_path):
    if os.path.exists(metadata_path):
    with open(metadata_path, "r") as f:
    with open(metadata_path, "r") as f:
    self.metadata = json.load(f)
    self.metadata = json.load(f)


    if self.metadata:
    if self.metadata:
    logger.info(f"Loaded metadata: {list(self.metadata.keys())}")
    logger.info(f"Loaded metadata: {list(self.metadata.keys())}")


except Exception as e:
except Exception as e:
    logger.warning(f"Error loading metadata: {e}")
    logger.warning(f"Error loading metadata: {e}")


    def _load_tokenizer(self) -> None:
    def _load_tokenizer(self) -> None:
    """
    """
    Load the tokenizer for text models.
    Load the tokenizer for text models.
    """
    """
    if not TRANSFORMERS_AVAILABLE:
    if not TRANSFORMERS_AVAILABLE:
    logger.warning("Transformers not available. Cannot load tokenizer.")
    logger.warning("Transformers not available. Cannot load tokenizer.")
    return try:
    return try:
    # Determine tokenizer path
    # Determine tokenizer path
    tokenizer_path = self.tokenizer_path
    tokenizer_path = self.tokenizer_path
    if not tokenizer_path:
    if not tokenizer_path:
    # Check if tokenizer is in the same directory as the model
    # Check if tokenizer is in the same directory as the model
    model_dir = os.path.dirname(self.model_path)
    model_dir = os.path.dirname(self.model_path)
    if os.path.exists(os.path.join(model_dir, "tokenizer.json")):
    if os.path.exists(os.path.join(model_dir, "tokenizer.json")):
    tokenizer_path = model_dir
    tokenizer_path = model_dir
    elif "tokenizer" in self.metadata:
    elif "tokenizer" in self.metadata:
    tokenizer_path = self.metadata["tokenizer"]
    tokenizer_path = self.metadata["tokenizer"]
    else:
    else:
    # Try to infer from model name
    # Try to infer from model name
    model_name = os.path.basename(self.model_path)
    model_name = os.path.basename(self.model_path)
    if "gpt" in model_name.lower():
    if "gpt" in model_name.lower():
    tokenizer_path = "gpt2"
    tokenizer_path = "gpt2"
    elif "bert" in model_name.lower():
    elif "bert" in model_name.lower():
    tokenizer_path = "bert-base-uncased"
    tokenizer_path = "bert-base-uncased"
    elif "t5" in model_name.lower():
    elif "t5" in model_name.lower():
    tokenizer_path = "t5-small"
    tokenizer_path = "t5-small"
    else:
    else:
    logger.warning(
    logger.warning(
    "Could not determine tokenizer. Please specify tokenizer_path."
    "Could not determine tokenizer. Please specify tokenizer_path."
    )
    )
    return # Load tokenizer
    return # Load tokenizer
    self.tokenizer = AutoTokenizer.from_pretrained(tokenizer_path)
    self.tokenizer = AutoTokenizer.from_pretrained(tokenizer_path)
    logger.info(f"Loaded tokenizer from {tokenizer_path}")
    logger.info(f"Loaded tokenizer from {tokenizer_path}")


except Exception as e:
except Exception as e:
    logger.warning(f"Error loading tokenizer: {e}")
    logger.warning(f"Error loading tokenizer: {e}")


    def generate_text(
    def generate_text(
    self,
    self,
    prompt: str,
    prompt: str,
    max_length: int = 100,
    max_length: int = 100,
    temperature: float = 0.7,
    temperature: float = 0.7,
    top_p: float = 0.9,
    top_p: float = 0.9,
    top_k: int = 50,
    top_k: int = 50,
    **kwargs,
    **kwargs,
    ) -> str:
    ) -> str:
    """
    """
    Generate text using the ONNX model.
    Generate text using the ONNX model.


    Args:
    Args:
    prompt: Input prompt
    prompt: Input prompt
    max_length: Maximum length of generated text
    max_length: Maximum length of generated text
    temperature: Temperature for sampling
    temperature: Temperature for sampling
    top_p: Top-p sampling parameter
    top_p: Top-p sampling parameter
    top_k: Top-k sampling parameter
    top_k: Top-k sampling parameter
    **kwargs: Additional parameters for text generation
    **kwargs: Additional parameters for text generation


    Returns:
    Returns:
    Generated text
    Generated text
    """
    """
    if not self.session:
    if not self.session:
    self.load()
    self.load()


    if not self.tokenizer:
    if not self.tokenizer:
    raise ValueError("Tokenizer not available. Cannot generate text.")
    raise ValueError("Tokenizer not available. Cannot generate text.")


    try:
    try:
    # Tokenize input
    # Tokenize input
    inputs = self.tokenizer(prompt, return_tensors="pt")
    inputs = self.tokenizer(prompt, return_tensors="pt")
    input_ids = inputs["input_ids"].numpy()
    input_ids = inputs["input_ids"].numpy()
    attention_mask = inputs["attention_mask"].numpy()
    attention_mask = inputs["attention_mask"].numpy()


    # Prepare inputs for the model
    # Prepare inputs for the model
    onnx_inputs = {}
    onnx_inputs = {}


    # Map inputs based on model's expected input names
    # Map inputs based on model's expected input names
    if "input_ids" in self.input_names:
    if "input_ids" in self.input_names:
    onnx_inputs["input_ids"] = input_ids
    onnx_inputs["input_ids"] = input_ids


    if "attention_mask" in self.input_names:
    if "attention_mask" in self.input_names:
    onnx_inputs["attention_mask"] = attention_mask
    onnx_inputs["attention_mask"] = attention_mask


    # Add generation parameters if the model supports them
    # Add generation parameters if the model supports them
    if "max_length" in self.input_names:
    if "max_length" in self.input_names:
    onnx_inputs["max_length"] = np.array([max_length], dtype=np.int64)
    onnx_inputs["max_length"] = np.array([max_length], dtype=np.int64)


    if "temperature" in self.input_names:
    if "temperature" in self.input_names:
    onnx_inputs["temperature"] = np.array([temperature], dtype=np.float32)
    onnx_inputs["temperature"] = np.array([temperature], dtype=np.float32)


    if "top_p" in self.input_names:
    if "top_p" in self.input_names:
    onnx_inputs["top_p"] = np.array([top_p], dtype=np.float32)
    onnx_inputs["top_p"] = np.array([top_p], dtype=np.float32)


    if "top_k" in self.input_names:
    if "top_k" in self.input_names:
    onnx_inputs["top_k"] = np.array([top_k], dtype=np.int64)
    onnx_inputs["top_k"] = np.array([top_k], dtype=np.int64)


    # Run inference
    # Run inference
    outputs = self.session.run(self.output_names, onnx_inputs)
    outputs = self.session.run(self.output_names, onnx_inputs)


    # Process outputs based on model type
    # Process outputs based on model type
    if self.model_type == "text-generation":
    if self.model_type == "text-generation":
    # Get output IDs
    # Get output IDs
    output_ids = outputs[0]
    output_ids = outputs[0]


    # Decode output
    # Decode output
    if output_ids.ndim > 1:
    if output_ids.ndim > 1:
    output_text = self.tokenizer.decode(
    output_text = self.tokenizer.decode(
    output_ids[0], skip_special_tokens=True
    output_ids[0], skip_special_tokens=True
    )
    )
    else:
    else:
    output_text = self.tokenizer.decode(
    output_text = self.tokenizer.decode(
    output_ids, skip_special_tokens=True
    output_ids, skip_special_tokens=True
    )
    )


    return output_text
    return output_text


    else:
    else:
    # For other model types, return raw outputs
    # For other model types, return raw outputs
    return str(outputs)
    return str(outputs)


except Exception as e:
except Exception as e:
    logger.error(f"Error generating text: {e}")
    logger.error(f"Error generating text: {e}")
    raise
    raise


    def classify_text(self, text: str, **kwargs) -> Dict[str, float]:
    def classify_text(self, text: str, **kwargs) -> Dict[str, float]:
    """
    """
    Classify text using the ONNX model.
    Classify text using the ONNX model.


    Args:
    Args:
    text: Input text
    text: Input text
    **kwargs: Additional parameters for classification
    **kwargs: Additional parameters for classification


    Returns:
    Returns:
    Dictionary of class labels and scores
    Dictionary of class labels and scores
    """
    """
    if not self.session:
    if not self.session:
    self.load()
    self.load()


    if not self.tokenizer:
    if not self.tokenizer:
    raise ValueError("Tokenizer not available. Cannot classify text.")
    raise ValueError("Tokenizer not available. Cannot classify text.")


    try:
    try:
    # Tokenize input
    # Tokenize input
    inputs = self.tokenizer(text, return_tensors="pt")
    inputs = self.tokenizer(text, return_tensors="pt")
    input_ids = inputs["input_ids"].numpy()
    input_ids = inputs["input_ids"].numpy()
    attention_mask = inputs["attention_mask"].numpy()
    attention_mask = inputs["attention_mask"].numpy()


    # Prepare inputs for the model
    # Prepare inputs for the model
    onnx_inputs = {}
    onnx_inputs = {}


    # Map inputs based on model's expected input names
    # Map inputs based on model's expected input names
    if "input_ids" in self.input_names:
    if "input_ids" in self.input_names:
    onnx_inputs["input_ids"] = input_ids
    onnx_inputs["input_ids"] = input_ids


    if "attention_mask" in self.input_names:
    if "attention_mask" in self.input_names:
    onnx_inputs["attention_mask"] = attention_mask
    onnx_inputs["attention_mask"] = attention_mask


    # Run inference
    # Run inference
    outputs = self.session.run(self.output_names, onnx_inputs)
    outputs = self.session.run(self.output_names, onnx_inputs)


    # Process outputs
    # Process outputs
    logits = outputs[0]
    logits = outputs[0]


    # Convert logits to probabilities
    # Convert logits to probabilities
    if TORCH_AVAILABLE:
    if TORCH_AVAILABLE:
    probs = torch.nn.functional.softmax(
    probs = torch.nn.functional.softmax(
    torch.tensor(logits), dim=-1
    torch.tensor(logits), dim=-1
    ).numpy()
    ).numpy()
    else:
    else:
    # Manual softmax
    # Manual softmax
    exp_logits = np.exp(logits - np.max(logits, axis=-1, keepdims=True))
    exp_logits = np.exp(logits - np.max(logits, axis=-1, keepdims=True))
    probs = exp_logits / np.sum(exp_logits, axis=-1, keepdims=True)
    probs = exp_logits / np.sum(exp_logits, axis=-1, keepdims=True)


    # Get class labels if available
    # Get class labels if available
    labels = []
    labels = []
    if "id2label" in self.metadata:
    if "id2label" in self.metadata:
    id2label = json.loads(self.metadata["id2label"])
    id2label = json.loads(self.metadata["id2label"])
    labels = [
    labels = [
    id2label.get(str(i), f"Class {i}") for i in range(probs.shape[-1])
    id2label.get(str(i), f"Class {i}") for i in range(probs.shape[-1])
    ]
    ]
    else:
    else:
    labels = [f"Class {i}" for i in range(probs.shape[-1])]
    labels = [f"Class {i}" for i in range(probs.shape[-1])]


    # Create result dictionary
    # Create result dictionary
    result = {label: float(prob) for label, prob in zip(labels, probs[0])}
    result = {label: float(prob) for label, prob in zip(labels, probs[0])}


    return result
    return result


except Exception as e:
except Exception as e:
    logger.error(f"Error classifying text: {e}")
    logger.error(f"Error classifying text: {e}")
    raise
    raise


    def encode(self, texts: Union[str, List[str]], **kwargs) -> np.ndarray:
    def encode(self, texts: Union[str, List[str]], **kwargs) -> np.ndarray:
    """
    """
    Generate embeddings for text using the ONNX model.
    Generate embeddings for text using the ONNX model.


    Args:
    Args:
    texts: Input text or list of texts
    texts: Input text or list of texts
    **kwargs: Additional parameters for encoding
    **kwargs: Additional parameters for encoding


    Returns:
    Returns:
    Numpy array of embeddings
    Numpy array of embeddings
    """
    """
    if not self.session:
    if not self.session:
    self.load()
    self.load()


    if not self.tokenizer:
    if not self.tokenizer:
    raise ValueError("Tokenizer not available. Cannot encode text.")
    raise ValueError("Tokenizer not available. Cannot encode text.")


    try:
    try:
    # Handle single text or list of texts
    # Handle single text or list of texts
    if isinstance(texts, str):
    if isinstance(texts, str):
    texts = [texts]
    texts = [texts]


    # Tokenize input
    # Tokenize input
    inputs = self.tokenizer(
    inputs = self.tokenizer(
    texts, padding=True, truncation=True, return_tensors="pt"
    texts, padding=True, truncation=True, return_tensors="pt"
    )
    )


    input_ids = inputs["input_ids"].numpy()
    input_ids = inputs["input_ids"].numpy()
    attention_mask = inputs["attention_mask"].numpy()
    attention_mask = inputs["attention_mask"].numpy()


    # Prepare inputs for the model
    # Prepare inputs for the model
    onnx_inputs = {}
    onnx_inputs = {}


    # Map inputs based on model's expected input names
    # Map inputs based on model's expected input names
    if "input_ids" in self.input_names:
    if "input_ids" in self.input_names:
    onnx_inputs["input_ids"] = input_ids
    onnx_inputs["input_ids"] = input_ids


    if "attention_mask" in self.input_names:
    if "attention_mask" in self.input_names:
    onnx_inputs["attention_mask"] = attention_mask
    onnx_inputs["attention_mask"] = attention_mask


    # Run inference
    # Run inference
    outputs = self.session.run(self.output_names, onnx_inputs)
    outputs = self.session.run(self.output_names, onnx_inputs)


    # Process outputs
    # Process outputs
    embeddings = outputs[0]
    embeddings = outputs[0]


    # Normalize embeddings if requested
    # Normalize embeddings if requested
    if kwargs.get("normalize", True):
    if kwargs.get("normalize", True):
    if TORCH_AVAILABLE:
    if TORCH_AVAILABLE:
    embeddings = torch.nn.functional.normalize(
    embeddings = torch.nn.functional.normalize(
    torch.tensor(embeddings), p=2, dim=1
    torch.tensor(embeddings), p=2, dim=1
    ).numpy()
    ).numpy()
    else:
    else:
    # Manual normalization
    # Manual normalization
    norms = np.sqrt(np.sum(embeddings**2, axis=1, keepdims=True))
    norms = np.sqrt(np.sum(embeddings**2, axis=1, keepdims=True))
    embeddings = embeddings / norms
    embeddings = embeddings / norms


    return embeddings
    return embeddings


except Exception as e:
except Exception as e:
    logger.error(f"Error encoding text: {e}")
    logger.error(f"Error encoding text: {e}")
    raise
    raise


    def classify_image(self, image_path: str, **kwargs) -> Dict[str, float]:
    def classify_image(self, image_path: str, **kwargs) -> Dict[str, float]:
    """
    """
    Classify an image using the ONNX model.
    Classify an image using the ONNX model.


    Args:
    Args:
    image_path: Path to the image file
    image_path: Path to the image file
    **kwargs: Additional parameters for classification
    **kwargs: Additional parameters for classification


    Returns:
    Returns:
    Dictionary of class labels and scores
    Dictionary of class labels and scores
    """
    """
    if not self.session:
    if not self.session:
    self.load()
    self.load()


    try:
    try:
    # Load and preprocess image
    # Load and preprocess image
    image_data = self._preprocess_image(image_path)
    image_data = self._preprocess_image(image_path)


    # Prepare inputs for the model
    # Prepare inputs for the model
    onnx_inputs = {}
    onnx_inputs = {}


    # Map inputs based on model's expected input names
    # Map inputs based on model's expected input names
    if len(self.input_names) == 1:
    if len(self.input_names) == 1:
    # If there's only one input, use it directly
    # If there's only one input, use it directly
    onnx_inputs[self.input_names[0]] = image_data
    onnx_inputs[self.input_names[0]] = image_data
    else:
    else:
    # Try to map to common input names
    # Try to map to common input names
    if "input" in self.input_names:
    if "input" in self.input_names:
    onnx_inputs["input"] = image_data
    onnx_inputs["input"] = image_data
    elif "images" in self.input_names:
    elif "images" in self.input_names:
    onnx_inputs["images"] = image_data
    onnx_inputs["images"] = image_data
    elif "pixel_values" in self.input_names:
    elif "pixel_values" in self.input_names:
    onnx_inputs["pixel_values"] = image_data
    onnx_inputs["pixel_values"] = image_data
    else:
    else:
    # Use the first input name
    # Use the first input name
    onnx_inputs[self.input_names[0]] = image_data
    onnx_inputs[self.input_names[0]] = image_data


    # Run inference
    # Run inference
    outputs = self.session.run(self.output_names, onnx_inputs)
    outputs = self.session.run(self.output_names, onnx_inputs)


    # Process outputs
    # Process outputs
    logits = outputs[0]
    logits = outputs[0]


    # Convert logits to probabilities
    # Convert logits to probabilities
    if TORCH_AVAILABLE:
    if TORCH_AVAILABLE:
    probs = torch.nn.functional.softmax(
    probs = torch.nn.functional.softmax(
    torch.tensor(logits), dim=-1
    torch.tensor(logits), dim=-1
    ).numpy()
    ).numpy()
    else:
    else:
    # Manual softmax
    # Manual softmax
    exp_logits = np.exp(logits - np.max(logits, axis=-1, keepdims=True))
    exp_logits = np.exp(logits - np.max(logits, axis=-1, keepdims=True))
    probs = exp_logits / np.sum(exp_logits, axis=-1, keepdims=True)
    probs = exp_logits / np.sum(exp_logits, axis=-1, keepdims=True)


    # Get class labels if available
    # Get class labels if available
    labels = []
    labels = []
    if "id2label" in self.metadata:
    if "id2label" in self.metadata:
    id2label = json.loads(self.metadata["id2label"])
    id2label = json.loads(self.metadata["id2label"])
    labels = [
    labels = [
    id2label.get(str(i), f"Class {i}") for i in range(probs.shape[-1])
    id2label.get(str(i), f"Class {i}") for i in range(probs.shape[-1])
    ]
    ]
    else:
    else:
    # Try to load ImageNet labels if it's a common image classification model
    # Try to load ImageNet labels if it's a common image classification model
    try:
    try:
    = list_models()
    = list_models()
except Exception:
except Exception:
    labels = [f"Class {i}" for i in range(probs.shape[-1])]
    labels = [f"Class {i}" for i in range(probs.shape[-1])]


    # Create result dictionary
    # Create result dictionary
    result = {label: float(prob) for label, prob in zip(labels, probs[0])}
    result = {label: float(prob) for label, prob in zip(labels, probs[0])}


    return result
    return result


except Exception as e:
except Exception as e:
    logger.error(f"Error classifying image: {e}")
    logger.error(f"Error classifying image: {e}")
    raise
    raise


    def _preprocess_image(self, image_path: str) -> np.ndarray:
    def _preprocess_image(self, image_path: str) -> np.ndarray:
    """
    """
    Preprocess an image for the model.
    Preprocess an image for the model.


    Args:
    Args:
    image_path: Path to the image file
    image_path: Path to the image file


    Returns:
    Returns:
    Preprocessed image as numpy array
    Preprocessed image as numpy array
    """
    """
    try:
    try:
    # Try to use PIL for image loading
    # Try to use PIL for image loading
    # Load image
    # Load image
    image = Image.open(image_path).convert("RGB")
    image = Image.open(image_path).convert("RGB")


    # Resize image
    # Resize image
    input_shape = self.session.get_inputs()[0].shape
    input_shape = self.session.get_inputs()[0].shape
    if len(input_shape) == 4:
    if len(input_shape) == 4:
    # NCHW format
    # NCHW format
    height, width = input_shape[2], input_shape[3]
    height, width = input_shape[2], input_shape[3]
    else:
    else:
    # Default to 224x224
    # Default to 224x224
    height, width = 224, 224
    height, width = 224, 224


    image = image.resize((width, height))
    image = image.resize((width, height))


    # Convert to numpy array
    # Convert to numpy array
    image_data = np.array(image).astype(np.float32)
    image_data = np.array(image).astype(np.float32)


    # Normalize
    # Normalize
    image_data = image_data / 255.0
    image_data = image_data / 255.0
    mean = np.array([0.485, 0.456, 0.406]).reshape(1, 1, 3)
    mean = np.array([0.485, 0.456, 0.406]).reshape(1, 1, 3)
    std = np.array([0.229, 0.224, 0.225]).reshape(1, 1, 3)
    std = np.array([0.229, 0.224, 0.225]).reshape(1, 1, 3)
    image_data = (image_data - mean) / std
    image_data = (image_data - mean) / std


    # Transpose from HWC to CHW
    # Transpose from HWC to CHW
    image_data = image_data.transpose(2, 0, 1)
    image_data = image_data.transpose(2, 0, 1)


    # Add batch dimension
    # Add batch dimension
    image_data = np.expand_dims(image_data, axis=0)
    image_data = np.expand_dims(image_data, axis=0)


    return image_data
    return image_data


except Exception as e:
except Exception as e:
    logger.error(f"Error preprocessing image: {e}")
    logger.error(f"Error preprocessing image: {e}")
    raise
    raise


    def get_metadata(self) -> Dict[str, Any]:
    def get_metadata(self) -> Dict[str, Any]:
    """
    """
    Get metadata about the model.
    Get metadata about the model.


    Returns:
    Returns:
    Dictionary with model metadata
    Dictionary with model metadata
    """
    """
    if not self.session:
    if not self.session:
    self.load()
    self.load()


    metadata = {
    metadata = {
    "model_path": self.model_path,
    "model_path": self.model_path,
    "model_type": self.model_type,
    "model_type": self.model_type,
    "providers": self.providers,
    "providers": self.providers,
    "input_names": self.input_names,
    "input_names": self.input_names,
    "output_names": self.output_names,
    "output_names": self.output_names,
    "custom_metadata": self.metadata,
    "custom_metadata": self.metadata,
    }
    }


    # Add model metadata
    # Add model metadata
    model_meta = self.session.get_modelmeta()
    model_meta = self.session.get_modelmeta()
    if model_meta:
    if model_meta:
    metadata["description"] = model_meta.description
    metadata["description"] = model_meta.description
    metadata["domain"] = model_meta.domain
    metadata["domain"] = model_meta.domain
    metadata["graph_name"] = model_meta.graph_name
    metadata["graph_name"] = model_meta.graph_name
    metadata["producer_name"] = model_meta.producer_name
    metadata["producer_name"] = model_meta.producer_name
    metadata["version"] = model_meta.version
    metadata["version"] = model_meta.version


    return metadata
    return metadata




    # Example usage
    # Example usage
    if __name__ == "__main__":
    if __name__ == "__main__":
    # Check if ONNX Runtime is available
    # Check if ONNX Runtime is available
    if not ONNX_AVAILABLE:
    if not ONNX_AVAILABLE:
    print(
    print(
    "ONNX Runtime not available. Please install it with: pip install onnxruntime"
    "ONNX Runtime not available. Please install it with: pip install onnxruntime"
    )
    )
    exit(1)
    exit(1)


    # Example model path (replace with an actual ONNX model path)
    # Example model path (replace with an actual ONNX model path)
    model_path = "path/to/model.onnx"
    model_path = "path/to/model.onnx"


    if os.path.exists(model_path):
    if os.path.exists(model_path):
    # Create ONNX model
    # Create ONNX model
    model = ONNXModel(model_path=model_path, model_type="text-generation")
    model = ONNXModel(model_path=model_path, model_type="text-generation")


    # Load the model
    # Load the model
    model.load()
    model.load()


    # Get metadata
    # Get metadata
    metadata = model.get_metadata()
    metadata = model.get_metadata()
    print("Model Metadata:")
    print("Model Metadata:")
    for key, value in metadata.items():
    for key, value in metadata.items():
    print(f"  {key}: {value}")
    print(f"  {key}: {value}")


    # Generate text
    # Generate text
    if model.tokenizer:
    if model.tokenizer:
    prompt = "Hello, world!"
    prompt = "Hello, world!"
    print(f"\nGenerating text for prompt: {prompt}")
    print(f"\nGenerating text for prompt: {prompt}")
    output = model.generate_text(prompt)
    output = model.generate_text(prompt)
    print(f"Output: {output}")
    print(f"Output: {output}")
    else:
    else:
    print(f"Model file not found: {model_path}")
    print(f"Model file not found: {model_path}")
    print("Please specify a valid ONNX model path.")
    print("Please specify a valid ONNX model path.")