"""
"""
Vision model implementation for the AI Models module.
Vision model implementation for the AI Models module.


This module provides specialized classes for working with vision models,
This module provides specialized classes for working with vision models,
including image classification, object detection, and image generation.
including image classification, object detection, and image generation.
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
    from typing import Any, Dict, List, Optional
    from typing import Any, Dict, List, Optional


    import numpy as np
    import numpy as np
    import torch
    import torch
    from torch import nn
    from torch import nn


    TORCH_AVAILABLE
    TORCH_AVAILABLE
    import transformers
    import transformers
    from transformers import (AutoImageProcessor,
    from transformers import (AutoImageProcessor,
    AutoModelForImageClassification)
    AutoModelForImageClassification)


    TRANSFORMERS_AVAILABLE
    TRANSFORMERS_AVAILABLE
    from PIL import Image
    from PIL import Image


    PIL_AVAILABLE
    PIL_AVAILABLE
    import cv2
    import cv2
    import onnxruntime
    import onnxruntime
    from transformers import AutoModelForObjectDetection
    from transformers import AutoModelForObjectDetection


    self.processor
    self.processor
    from transformers import AutoModelForImageSegmentation
    from transformers import AutoModelForImageSegmentation


    self.processor
    self.processor
    from transformers import (AutoModelForVision2Seq,
    from transformers import (AutoModelForVision2Seq,
    ViTImageProcessor)
    ViTImageProcessor)


    self.processor
    self.processor
    from torchvision.models import resnet50
    from torchvision.models import resnet50


    self.model
    self.model
    from transformers import ViTForImageClassification
    from transformers import ViTForImageClassification


    self.model
    self.model
    from transformers import AutoModelForImageClassification
    from transformers import AutoModelForImageClassification


    if isinstance
    if isinstance
    from torchvision import transforms
    from torchvision import transforms






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


    = True
    = True
except ImportError:
except ImportError:
    logger.warning("PyTorch not available. Vision model support will be limited.")
    logger.warning("PyTorch not available. Vision model support will be limited.")
    TORCH_AVAILABLE = False
    TORCH_AVAILABLE = False


    try:
    try:


    = True
    = True
except ImportError:
except ImportError:
    logger.warning("Transformers not available. Vision model support will be limited.")
    logger.warning("Transformers not available. Vision model support will be limited.")
    TRANSFORMERS_AVAILABLE = False
    TRANSFORMERS_AVAILABLE = False


    try:
    try:
    = True
    = True
except ImportError:
except ImportError:
    logger.warning("PIL not available. Image processing will be limited.")
    logger.warning("PIL not available. Image processing will be limited.")
    PIL_AVAILABLE = False
    PIL_AVAILABLE = False


    try:
    try:




    CV2_AVAILABLE = True
    CV2_AVAILABLE = True
except ImportError:
except ImportError:
    logger.warning("OpenCV not available. Some vision features will be limited.")
    logger.warning("OpenCV not available. Some vision features will be limited.")
    CV2_AVAILABLE = False
    CV2_AVAILABLE = False


    try:
    try:
    as ort
    as ort


    ONNX_AVAILABLE = True
    ONNX_AVAILABLE = True
except ImportError:
except ImportError:
    logger.warning(
    logger.warning(
    "ONNX Runtime not available. ONNX vision model support will be limited."
    "ONNX Runtime not available. ONNX vision model support will be limited."
    )
    )
    ONNX_AVAILABLE = False
    ONNX_AVAILABLE = False




    class VisionModel:
    class VisionModel:
    """
    """
    Class for working with vision models.
    Class for working with vision models.
    """
    """


    def __init__(
    def __init__(
    self,
    self,
    model_path: str,
    model_path: str,
    model_type: str = "image-classification",
    model_type: str = "image-classification",
    processor_path: Optional[str] = None,
    processor_path: Optional[str] = None,
    device: str = "auto",
    device: str = "auto",
    **kwargs,
    **kwargs,
    ):
    ):
    """
    """
    Initialize a vision model.
    Initialize a vision model.


    Args:
    Args:
    model_path: Path to the model file or directory
    model_path: Path to the model file or directory
    model_type: Type of model (image-classification, object-detection, etc.)
    model_type: Type of model (image-classification, object-detection, etc.)
    processor_path: Optional path to the image processor
    processor_path: Optional path to the image processor
    device: Device to run the model on (auto, cpu, cuda, etc.)
    device: Device to run the model on (auto, cpu, cuda, etc.)
    **kwargs: Additional parameters for model initialization
    **kwargs: Additional parameters for model initialization
    """
    """
    self.model_path = model_path
    self.model_path = model_path
    self.model_type = model_type
    self.model_type = model_type
    self.processor_path = processor_path or model_path
    self.processor_path = processor_path or model_path
    self.device = device
    self.device = device
    self.kwargs = kwargs
    self.kwargs = kwargs
    self.model = None
    self.model = None
    self.processor = None
    self.processor = None


    # Determine the model format
    # Determine the model format
    self.model_format = self._detect_model_format()
    self.model_format = self._detect_model_format()


    # Determine device
    # Determine device
    if self.device == "auto":
    if self.device == "auto":
    if TORCH_AVAILABLE and torch.cuda.is_available():
    if TORCH_AVAILABLE and torch.cuda.is_available():
    self.device = "cuda"
    self.device = "cuda"
    else:
    else:
    self.device = "cpu"
    self.device = "cpu"


    logger.info(f"Initializing vision model: {model_path}")
    logger.info(f"Initializing vision model: {model_path}")
    logger.info(f"Model type: {model_type}")
    logger.info(f"Model type: {model_type}")
    logger.info(f"Model format: {self.model_format}")
    logger.info(f"Model format: {self.model_format}")
    logger.info(f"Device: {self.device}")
    logger.info(f"Device: {self.device}")


    def _detect_model_format(self) -> str:
    def _detect_model_format(self) -> str:
    """
    """
    Detect the format of the model.
    Detect the format of the model.


    Returns:
    Returns:
    Model format (huggingface, onnx, etc.)
    Model format (huggingface, onnx, etc.)
    """
    """
    if os.path.isdir(self.model_path):
    if os.path.isdir(self.model_path):
    # Check if it's a Hugging Face model
    # Check if it's a Hugging Face model
    if os.path.exists(os.path.join(self.model_path, "config.json")):
    if os.path.exists(os.path.join(self.model_path, "config.json")):
    return "huggingface"
    return "huggingface"
    else:
    else:
    # Check file extension
    # Check file extension
    file_ext = os.path.splitext(self.model_path)[1].lower()
    file_ext = os.path.splitext(self.model_path)[1].lower()
    if file_ext == ".onnx":
    if file_ext == ".onnx":
    return "onnx"
    return "onnx"
    elif file_ext in [".pt", ".pth"]:
    elif file_ext in [".pt", ".pth"]:
    return "pytorch"
    return "pytorch"
    elif file_ext == ".bin" and os.path.exists(
    elif file_ext == ".bin" and os.path.exists(
    os.path.join(os.path.dirname(self.model_path), "config.json")
    os.path.join(os.path.dirname(self.model_path), "config.json")
    ):
    ):
    return "huggingface"
    return "huggingface"


    # Default to huggingface
    # Default to huggingface
    return "huggingface"
    return "huggingface"


    def load(self) -> None:
    def load(self) -> None:
    """
    """
    Load the vision model.
    Load the vision model.
    """
    """
    if self.model_format == "huggingface":
    if self.model_format == "huggingface":
    self._load_huggingface_model()
    self._load_huggingface_model()
    elif self.model_format == "onnx":
    elif self.model_format == "onnx":
    self._load_onnx_model()
    self._load_onnx_model()
    elif self.model_format == "pytorch":
    elif self.model_format == "pytorch":
    self._load_pytorch_model()
    self._load_pytorch_model()
    else:
    else:
    raise ValueError(f"Unsupported model format: {self.model_format}")
    raise ValueError(f"Unsupported model format: {self.model_format}")


    def _load_huggingface_model(self) -> None:
    def _load_huggingface_model(self) -> None:
    """
    """
    Load a Hugging Face vision model.
    Load a Hugging Face vision model.
    """
    """
    if not TRANSFORMERS_AVAILABLE:
    if not TRANSFORMERS_AVAILABLE:
    raise ImportError(
    raise ImportError(
    "Transformers not available. Please install it with: pip install transformers"
    "Transformers not available. Please install it with: pip install transformers"
    )
    )


    if not TORCH_AVAILABLE:
    if not TORCH_AVAILABLE:
    raise ImportError(
    raise ImportError(
    "PyTorch not available. Please install it with: pip install torch"
    "PyTorch not available. Please install it with: pip install torch"
    )
    )


    logger.info(f"Loading Hugging Face vision model: {self.model_path}")
    logger.info(f"Loading Hugging Face vision model: {self.model_path}")


    try:
    try:
    # Load processor
    # Load processor
    if self.model_type == "image-classification":
    if self.model_type == "image-classification":
    self.processor = AutoImageProcessor.from_pretrained(self.processor_path)
    self.processor = AutoImageProcessor.from_pretrained(self.processor_path)
    self.model = AutoModelForImageClassification.from_pretrained(
    self.model = AutoModelForImageClassification.from_pretrained(
    self.model_path, **self.kwargs
    self.model_path, **self.kwargs
    )
    )
    elif self.model_type == "object-detection":
    elif self.model_type == "object-detection":
    = AutoImageProcessor.from_pretrained(self.processor_path)
    = AutoImageProcessor.from_pretrained(self.processor_path)
    self.model = AutoModelForObjectDetection.from_pretrained(
    self.model = AutoModelForObjectDetection.from_pretrained(
    self.model_path, **self.kwargs
    self.model_path, **self.kwargs
    )
    )
    elif self.model_type == "image-segmentation":
    elif self.model_type == "image-segmentation":
    = AutoImageProcessor.from_pretrained(self.processor_path)
    = AutoImageProcessor.from_pretrained(self.processor_path)
    self.model = AutoModelForImageSegmentation.from_pretrained(
    self.model = AutoModelForImageSegmentation.from_pretrained(
    self.model_path, **self.kwargs
    self.model_path, **self.kwargs
    )
    )
    elif self.model_type == "image-to-text":
    elif self.model_type == "image-to-text":
    = ViTImageProcessor.from_pretrained(self.processor_path)
    = ViTImageProcessor.from_pretrained(self.processor_path)
    self.model = AutoModelForVision2Seq.from_pretrained(
    self.model = AutoModelForVision2Seq.from_pretrained(
    self.model_path, **self.kwargs
    self.model_path, **self.kwargs
    )
    )
    else:
    else:
    raise ValueError(f"Unsupported model type: {self.model_type}")
    raise ValueError(f"Unsupported model type: {self.model_type}")


    # Move model to device
    # Move model to device
    self.model.to(self.device)
    self.model.to(self.device)


    logger.info(
    logger.info(
    f"Successfully loaded Hugging Face vision model: {self.model_path}"
    f"Successfully loaded Hugging Face vision model: {self.model_path}"
    )
    )


except Exception as e:
except Exception as e:
    logger.error(f"Error loading Hugging Face vision model: {e}")
    logger.error(f"Error loading Hugging Face vision model: {e}")
    raise
    raise


    def _load_onnx_model(self) -> None:
    def _load_onnx_model(self) -> None:
    """
    """
    Load an ONNX vision model.
    Load an ONNX vision model.
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


    logger.info(f"Loading ONNX vision model: {self.model_path}")
    logger.info(f"Loading ONNX vision model: {self.model_path}")


    try:
    try:
    # Configure session options
    # Configure session options
    session_options = ort.SessionOptions()
    session_options = ort.SessionOptions()
    session_options.graph_optimization_level = (
    session_options.graph_optimization_level = (
    ort.GraphOptimizationLevel.ORT_ENABLE_ALL
    ort.GraphOptimizationLevel.ORT_ENABLE_ALL
    )
    )


    # Determine providers
    # Determine providers
    if (
    if (
    self.device == "cuda"
    self.device == "cuda"
    and "CUDAExecutionProvider" in ort.get_available_providers()
    and "CUDAExecutionProvider" in ort.get_available_providers()
    ):
    ):
    providers = ["CUDAExecutionProvider", "CPUExecutionProvider"]
    providers = ["CUDAExecutionProvider", "CPUExecutionProvider"]
    else:
    else:
    providers = ["CPUExecutionProvider"]
    providers = ["CPUExecutionProvider"]


    # Create session
    # Create session
    self.model = ort.InferenceSession(
    self.model = ort.InferenceSession(
    self.model_path, sess_options=session_options, providers=providers
    self.model_path, sess_options=session_options, providers=providers
    )
    )


    # Get input and output names
    # Get input and output names
    self.input_names = [input.name for input in self.model.get_inputs()]
    self.input_names = [input.name for input in self.model.get_inputs()]
    self.output_names = [output.name for output in self.model.get_outputs()]
    self.output_names = [output.name for output in self.model.get_outputs()]


    logger.info(f"Successfully loaded ONNX vision model: {self.model_path}")
    logger.info(f"Successfully loaded ONNX vision model: {self.model_path}")
    logger.info(f"Model inputs: {self.input_names}")
    logger.info(f"Model inputs: {self.input_names}")
    logger.info(f"Model outputs: {self.output_names}")
    logger.info(f"Model outputs: {self.output_names}")


    # Try to load labels if available
    # Try to load labels if available
    self._load_labels()
    self._load_labels()


except Exception as e:
except Exception as e:
    logger.error(f"Error loading ONNX vision model: {e}")
    logger.error(f"Error loading ONNX vision model: {e}")
    raise
    raise


    def _load_pytorch_model(self) -> None:
    def _load_pytorch_model(self) -> None:
    """
    """
    Load a PyTorch vision model.
    Load a PyTorch vision model.
    """
    """
    if not TORCH_AVAILABLE:
    if not TORCH_AVAILABLE:
    raise ImportError(
    raise ImportError(
    "PyTorch not available. Please install it with: pip install torch"
    "PyTorch not available. Please install it with: pip install torch"
    )
    )


    logger.info(f"Loading PyTorch vision model: {self.model_path}")
    logger.info(f"Loading PyTorch vision model: {self.model_path}")


    try:
    try:
    # Load model
    # Load model
    self.model = torch.load(self.model_path, map_location=self.device)
    self.model = torch.load(self.model_path, map_location=self.device)


    # If it's a state dict, try to load it into a model
    # If it's a state dict, try to load it into a model
    if isinstance(self.model, dict):
    if isinstance(self.model, dict):
    # Try to determine the model architecture
    # Try to determine the model architecture
    if "model_type" in self.kwargs:
    if "model_type" in self.kwargs:
    model_type = self.kwargs["model_type"]
    model_type = self.kwargs["model_type"]
    if model_type == "resnet":
    if model_type == "resnet":
    = resnet50()
    = resnet50()
    elif model_type == "vit":
    elif model_type == "vit":
    = ViTForImageClassification.from_pretrained(
    = ViTForImageClassification.from_pretrained(
    "google/vit-base-patch16-224"
    "google/vit-base-patch16-224"
    )
    )
    else:
    else:
    raise ValueError(f"Unsupported model type: {model_type}")
    raise ValueError(f"Unsupported model type: {model_type}")


    # Load state dict
    # Load state dict
    self.model.load_state_dict(self.model)
    self.model.load_state_dict(self.model)
    else:
    else:
    logger.warning(
    logger.warning(
    "Model is a state dict but model_type not specified. Using as is."
    "Model is a state dict but model_type not specified. Using as is."
    )
    )


    # Move model to device
    # Move model to device
    if hasattr(self.model, "to"):
    if hasattr(self.model, "to"):
    self.model.to(self.device)
    self.model.to(self.device)


    # Set to evaluation mode
    # Set to evaluation mode
    if hasattr(self.model, "eval"):
    if hasattr(self.model, "eval"):
    self.model.eval()
    self.model.eval()


    logger.info(f"Successfully loaded PyTorch vision model: {self.model_path}")
    logger.info(f"Successfully loaded PyTorch vision model: {self.model_path}")


    # Try to load labels if available
    # Try to load labels if available
    self._load_labels()
    self._load_labels()


except Exception as e:
except Exception as e:
    logger.error(f"Error loading PyTorch vision model: {e}")
    logger.error(f"Error loading PyTorch vision model: {e}")
    raise
    raise


    def _load_labels(self) -> None:
    def _load_labels(self) -> None:
    """
    """
    Load class labels for the model.
    Load class labels for the model.
    """
    """
    # Try different label file formats
    # Try different label file formats
    label_files = [
    label_files = [
    os.path.join(os.path.dirname(self.model_path), "labels.json"),
    os.path.join(os.path.dirname(self.model_path), "labels.json"),
    os.path.join(os.path.dirname(self.model_path), "labels.txt"),
    os.path.join(os.path.dirname(self.model_path), "labels.txt"),
    os.path.join(os.path.dirname(self.model_path), "classes.json"),
    os.path.join(os.path.dirname(self.model_path), "classes.json"),
    os.path.join(os.path.dirname(self.model_path), "classes.txt"),
    os.path.join(os.path.dirname(self.model_path), "classes.txt"),
    ]
    ]


    for label_file in label_files:
    for label_file in label_files:
    if os.path.exists(label_file):
    if os.path.exists(label_file):
    try:
    try:
    if label_file.endswith(".json"):
    if label_file.endswith(".json"):
    with open(label_file, "r") as f:
    with open(label_file, "r") as f:
    self.labels = json.load(f)
    self.labels = json.load(f)
    else:
    else:
    with open(label_file, "r") as f:
    with open(label_file, "r") as f:
    self.labels = [line.strip() for line in f.readlines()]
    self.labels = [line.strip() for line in f.readlines()]


    logger.info(f"Loaded {len(self.labels)} labels from {label_file}")
    logger.info(f"Loaded {len(self.labels)} labels from {label_file}")
    return except Exception as e:
    return except Exception as e:
    logger.warning(f"Error loading labels from {label_file}: {e}")
    logger.warning(f"Error loading labels from {label_file}: {e}")


    # If no label file found, try to use ImageNet labels for common models
    # If no label file found, try to use ImageNet labels for common models
    try:
    try:
    if TRANSFORMERS_AVAILABLE:
    if TRANSFORMERS_AVAILABLE:
    (self.model, AutoModelForImageClassification):
    (self.model, AutoModelForImageClassification):
    self.labels = list(self.model.config.id2label.values())
    self.labels = list(self.model.config.id2label.values())
    logger.info(f"Using {len(self.labels)} labels from model config")
    logger.info(f"Using {len(self.labels)} labels from model config")
    return except Exception:
    return except Exception:
    pass
    pass


    logger.warning("No labels found for the model")
    logger.warning("No labels found for the model")
    self.labels = None
    self.labels = None


    def classify_image(self, image_path: str, **kwargs) -> Dict[str, float]:
    def classify_image(self, image_path: str, **kwargs) -> Dict[str, float]:
    """
    """
    Classify an image using the vision model.
    Classify an image using the vision model.


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
    if not self.model:
    if not self.model:
    self.load()
    self.load()


    if not PIL_AVAILABLE:
    if not PIL_AVAILABLE:
    raise ImportError(
    raise ImportError(
    "PIL not available. Please install it with: pip install Pillow"
    "PIL not available. Please install it with: pip install Pillow"
    )
    )


    try:
    try:
    # Load image
    # Load image
    image = Image.open(image_path).convert("RGB")
    image = Image.open(image_path).convert("RGB")


    if self.model_format == "huggingface":
    if self.model_format == "huggingface":
    return self._classify_image_huggingface(image, **kwargs)
    return self._classify_image_huggingface(image, **kwargs)
    elif self.model_format == "onnx":
    elif self.model_format == "onnx":
    return self._classify_image_onnx(image, **kwargs)
    return self._classify_image_onnx(image, **kwargs)
    elif self.model_format == "pytorch":
    elif self.model_format == "pytorch":
    return self._classify_image_pytorch(image, **kwargs)
    return self._classify_image_pytorch(image, **kwargs)
    else:
    else:
    raise ValueError(f"Unsupported model format: {self.model_format}")
    raise ValueError(f"Unsupported model format: {self.model_format}")


except Exception as e:
except Exception as e:
    logger.error(f"Error classifying image: {e}")
    logger.error(f"Error classifying image: {e}")
    raise
    raise


    def _classify_image_huggingface(
    def _classify_image_huggingface(
    self, image: "Image.Image", **kwargs
    self, image: "Image.Image", **kwargs
    ) -> Dict[str, float]:
    ) -> Dict[str, float]:
    """
    """
    Classify an image using a Hugging Face vision model.
    Classify an image using a Hugging Face vision model.


    Args:
    Args:
    image: PIL Image
    image: PIL Image
    **kwargs: Additional parameters for classification
    **kwargs: Additional parameters for classification


    Returns:
    Returns:
    Dictionary of class labels and scores
    Dictionary of class labels and scores
    """
    """
    # Process image
    # Process image
    inputs = self.processor(images=image, return_tensors="pt").to(self.device)
    inputs = self.processor(images=image, return_tensors="pt").to(self.device)


    # Run inference
    # Run inference
    with torch.no_grad():
    with torch.no_grad():
    outputs = self.model(**inputs)
    outputs = self.model(**inputs)


    # Process outputs
    # Process outputs
    if self.model_type == "image-classification":
    if self.model_type == "image-classification":
    # Get logits
    # Get logits
    logits = outputs.logits
    logits = outputs.logits


    # Convert logits to probabilities
    # Convert logits to probabilities
    probs = torch.nn.functional.softmax(logits, dim=-1)[0].cpu().numpy()
    probs = torch.nn.functional.softmax(logits, dim=-1)[0].cpu().numpy()


    # Get class labels
    # Get class labels
    if hasattr(self.model.config, "id2label"):
    if hasattr(self.model.config, "id2label"):
    labels = list(self.model.config.id2label.values())
    labels = list(self.model.config.id2label.values())
    else:
    else:
    labels = [f"Class {i}" for i in range(len(probs))]
    labels = [f"Class {i}" for i in range(len(probs))]


    # Create result dictionary
    # Create result dictionary
    result = {label: float(prob) for label, prob in zip(labels, probs)}
    result = {label: float(prob) for label, prob in zip(labels, probs)}


    return result
    return result


    else:
    else:
    # For other model types, return raw outputs
    # For other model types, return raw outputs
    return {"outputs": str(outputs)}
    return {"outputs": str(outputs)}


    def _classify_image_onnx(self, image: "Image.Image", **kwargs) -> Dict[str, float]:
    def _classify_image_onnx(self, image: "Image.Image", **kwargs) -> Dict[str, float]:
    """
    """
    Classify an image using an ONNX vision model.
    Classify an image using an ONNX vision model.


    Args:
    Args:
    image: PIL Image
    image: PIL Image
    **kwargs: Additional parameters for classification
    **kwargs: Additional parameters for classification


    Returns:
    Returns:
    Dictionary of class labels and scores
    Dictionary of class labels and scores
    """
    """
    # Preprocess image
    # Preprocess image
    input_shape = self.model.get_inputs()[0].shape
    input_shape = self.model.get_inputs()[0].shape
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


    # Resize image
    # Resize image
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


    # Prepare inputs
    # Prepare inputs
    onnx_inputs = {self.input_names[0]: image_data}
    onnx_inputs = {self.input_names[0]: image_data}


    # Run inference
    # Run inference
    outputs = self.model.run(self.output_names, onnx_inputs)
    outputs = self.model.run(self.output_names, onnx_inputs)


    # Process outputs
    # Process outputs
    logits = outputs[0]
    logits = outputs[0]


    # Convert logits to probabilities
    # Convert logits to probabilities
    exp_logits = np.exp(logits - np.max(logits, axis=-1, keepdims=True))
    exp_logits = np.exp(logits - np.max(logits, axis=-1, keepdims=True))
    probs = exp_logits / np.sum(exp_logits, axis=-1, keepdims=True)
    probs = exp_logits / np.sum(exp_logits, axis=-1, keepdims=True)
    probs = probs[0]
    probs = probs[0]


    # Get class labels
    # Get class labels
    if self.labels:
    if self.labels:
    labels = self.labels
    labels = self.labels
    else:
    else:
    labels = [f"Class {i}" for i in range(len(probs))]
    labels = [f"Class {i}" for i in range(len(probs))]


    # Create result dictionary
    # Create result dictionary
    result = {label: float(prob) for label, prob in zip(labels, probs)}
    result = {label: float(prob) for label, prob in zip(labels, probs)}


    return result
    return result


    def _classify_image_pytorch(
    def _classify_image_pytorch(
    self, image: "Image.Image", **kwargs
    self, image: "Image.Image", **kwargs
    ) -> Dict[str, float]:
    ) -> Dict[str, float]:
    """
    """
    Classify an image using a PyTorch vision model.
    Classify an image using a PyTorch vision model.


    Args:
    Args:
    image: PIL Image
    image: PIL Image
    **kwargs: Additional parameters for classification
    **kwargs: Additional parameters for classification


    Returns:
    Returns:
    Dictionary of class labels and scores
    Dictionary of class labels and scores
    """
    """
    # Preprocess image
    # Preprocess image
    # Default transformation for common models
    # Default transformation for common models
    transform = transforms.Compose(
    transform = transforms.Compose(
    [
    [
    transforms.Resize(256),
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.ToTensor(),
    transforms.Normalize(
    transforms.Normalize(
    mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]
    mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]
    ),
    ),
    ]
    ]
    )
    )


    # Transform image
    # Transform image
    image_tensor = transform(image).unsqueeze(0).to(self.device)
    image_tensor = transform(image).unsqueeze(0).to(self.device)


    # Run inference
    # Run inference
    with torch.no_grad():
    with torch.no_grad():
    outputs = self.model(image_tensor)
    outputs = self.model(image_tensor)


    # Process outputs
    # Process outputs
    if isinstance(outputs, torch.Tensor):
    if isinstance(outputs, torch.Tensor):
    logits = outputs
    logits = outputs
    else:
    else:
    # Handle different output formats
    # Handle different output formats
    if hasattr(outputs, "logits"):
    if hasattr(outputs, "logits"):
    logits = outputs.logits
    logits = outputs.logits
    else:
    else:
    logits = list(outputs.values())[0]
    logits = list(outputs.values())[0]


    # Convert logits to probabilities
    # Convert logits to probabilities
    probs = torch.nn.functional.softmax(logits, dim=-1)[0].cpu().numpy()
    probs = torch.nn.functional.softmax(logits, dim=-1)[0].cpu().numpy()


    # Get class labels
    # Get class labels
    if self.labels:
    if self.labels:
    labels = self.labels
    labels = self.labels
    else:
    else:
    labels = [f"Class {i}" for i in range(len(probs))]
    labels = [f"Class {i}" for i in range(len(probs))]


    # Create result dictionary
    # Create result dictionary
    result = {label: float(prob) for label, prob in zip(labels, probs)}
    result = {label: float(prob) for label, prob in zip(labels, probs)}


    return result
    return result


    def detect_objects(
    def detect_objects(
    self, image_path: str, threshold: float = 0.5, **kwargs
    self, image_path: str, threshold: float = 0.5, **kwargs
    ) -> List[Dict[str, Any]]:
    ) -> List[Dict[str, Any]]:
    """
    """
    Detect objects in an image using the vision model.
    Detect objects in an image using the vision model.


    Args:
    Args:
    image_path: Path to the image file
    image_path: Path to the image file
    threshold: Confidence threshold for detections
    threshold: Confidence threshold for detections
    **kwargs: Additional parameters for object detection
    **kwargs: Additional parameters for object detection


    Returns:
    Returns:
    List of detected objects with bounding boxes and scores
    List of detected objects with bounding boxes and scores
    """
    """
    if not self.model:
    if not self.model:
    self.load()
    self.load()


    if not PIL_AVAILABLE:
    if not PIL_AVAILABLE:
    raise ImportError(
    raise ImportError(
    "PIL not available. Please install it with: pip install Pillow"
    "PIL not available. Please install it with: pip install Pillow"
    )
    )


    if self.model_type != "object-detection":
    if self.model_type != "object-detection":
    raise ValueError(
    raise ValueError(
    f"Model type {self.model_type} does not support object detection"
    f"Model type {self.model_type} does not support object detection"
    )
    )


    try:
    try:
    # Load image
    # Load image
    image = Image.open(image_path).convert("RGB")
    image = Image.open(image_path).convert("RGB")


    if self.model_format == "huggingface":
    if self.model_format == "huggingface":
    return self._detect_objects_huggingface(image, threshold, **kwargs)
    return self._detect_objects_huggingface(image, threshold, **kwargs)
    elif self.model_format == "onnx":
    elif self.model_format == "onnx":
    return self._detect_objects_onnx(image, threshold, **kwargs)
    return self._detect_objects_onnx(image, threshold, **kwargs)
    elif self.model_format == "pytorch":
    elif self.model_format == "pytorch":
    return self._detect_objects_pytorch(image, threshold, **kwargs)
    return self._detect_objects_pytorch(image, threshold, **kwargs)
    else:
    else:
    raise ValueError(f"Unsupported model format: {self.model_format}")
    raise ValueError(f"Unsupported model format: {self.model_format}")


except Exception as e:
except Exception as e:
    logger.error(f"Error detecting objects: {e}")
    logger.error(f"Error detecting objects: {e}")
    raise
    raise


    def _detect_objects_huggingface(
    def _detect_objects_huggingface(
    self, image: "Image.Image", threshold: float, **kwargs
    self, image: "Image.Image", threshold: float, **kwargs
    ) -> List[Dict[str, Any]]:
    ) -> List[Dict[str, Any]]:
    """
    """
    Detect objects in an image using a Hugging Face vision model.
    Detect objects in an image using a Hugging Face vision model.


    Args:
    Args:
    image: PIL Image
    image: PIL Image
    threshold: Confidence threshold for detections
    threshold: Confidence threshold for detections
    **kwargs: Additional parameters for object detection
    **kwargs: Additional parameters for object detection


    Returns:
    Returns:
    List of detected objects with bounding boxes and scores
    List of detected objects with bounding boxes and scores
    """
    """
    # Process image
    # Process image
    inputs = self.processor(images=image, return_tensors="pt").to(self.device)
    inputs = self.processor(images=image, return_tensors="pt").to(self.device)


    # Run inference
    # Run inference
    with torch.no_grad():
    with torch.no_grad():
    outputs = self.model(**inputs)
    outputs = self.model(**inputs)


    # Process outputs
    # Process outputs
    results = self.processor.post_process_object_detection(
    results = self.processor.post_process_object_detection(
    outputs, threshold=threshold, target_sizes=[(image.height, image.width)]
    outputs, threshold=threshold, target_sizes=[(image.height, image.width)]
    )[0]
    )[0]


    # Format results
    # Format results
    detections = []
    detections = []
    for score, label, box in zip(
    for score, label, box in zip(
    results["scores"], results["labels"], results["boxes"]
    results["scores"], results["labels"], results["boxes"]
    ):
    ):
    label_name = self.model.config.id2label[label.item()]
    label_name = self.model.config.id2label[label.item()]
    detection = {
    detection = {
    "label": label_name,
    "label": label_name,
    "score": float(score),
    "score": float(score),
    "box": {
    "box": {
    "x1": float(box[0]),
    "x1": float(box[0]),
    "y1": float(box[1]),
    "y1": float(box[1]),
    "x2": float(box[2]),
    "x2": float(box[2]),
    "y2": float(box[3]),
    "y2": float(box[3]),
    },
    },
    }
    }
    detections.append(detection)
    detections.append(detection)


    return detections
    return detections


    def _detect_objects_onnx(
    def _detect_objects_onnx(
    self, image: "Image.Image", threshold: float, **kwargs
    self, image: "Image.Image", threshold: float, **kwargs
    ) -> List[Dict[str, Any]]:
    ) -> List[Dict[str, Any]]:
    """
    """
    Detect objects in an image using an ONNX vision model.
    Detect objects in an image using an ONNX vision model.


    Args:
    Args:
    image: PIL Image
    image: PIL Image
    threshold: Confidence threshold for detections
    threshold: Confidence threshold for detections
    **kwargs: Additional parameters for object detection
    **kwargs: Additional parameters for object detection


    Returns:
    Returns:
    List of detected objects with bounding boxes and scores
    List of detected objects with bounding boxes and scores
    """
    """
    # This is a simplified implementation and may need to be adapted for specific models
    # This is a simplified implementation and may need to be adapted for specific models


    # Preprocess image
    # Preprocess image
    input_shape = self.model.get_inputs()[0].shape
    input_shape = self.model.get_inputs()[0].shape
    if len(input_shape) == 4:
    if len(input_shape) == 4:
    # NCHW format
    # NCHW format
    height, width = input_shape[2], input_shape[3]
    height, width = input_shape[2], input_shape[3]
    else:
    else:
    # Default to 640x640 (common for object detection)
    # Default to 640x640 (common for object detection)
    height, width = 640, 640
    height, width = 640, 640


    # Resize image
    # Resize image
    image_resized = image.resize((width, height))
    image_resized = image.resize((width, height))


    # Convert to numpy array
    # Convert to numpy array
    image_data = np.array(image_resized).astype(np.float32)
    image_data = np.array(image_resized).astype(np.float32)


    # Normalize
    # Normalize
    image_data = image_data / 255.0
    image_data = image_data / 255.0


    # Transpose from HWC to CHW
    # Transpose from HWC to CHW
    image_data = image_data.transpose(2, 0, 1)
    image_data = image_data.transpose(2, 0, 1)


    # Add batch dimension
    # Add batch dimension
    image_data = np.expand_dims(image_data, axis=0)
    image_data = np.expand_dims(image_data, axis=0)


    # Prepare inputs
    # Prepare inputs
    onnx_inputs = {self.input_names[0]: image_data}
    onnx_inputs = {self.input_names[0]: image_data}


    # Run inference
    # Run inference
    outputs = self.model.run(self.output_names, onnx_inputs)
    outputs = self.model.run(self.output_names, onnx_inputs)


    # Process outputs
    # Process outputs
    # The format of outputs depends on the specific model
    # The format of outputs depends on the specific model
    # This is a generic implementation that may need to be adapted
    # This is a generic implementation that may need to be adapted


    detections = []
    detections = []


    # Assuming outputs format: [batch_id, class_id, confidence, x1, y1, x2, y2]
    # Assuming outputs format: [batch_id, class_id, confidence, x1, y1, x2, y2]
    if len(outputs) > 0 and len(outputs[0].shape) == 2 and outputs[0].shape[1] >= 7:
    if len(outputs) > 0 and len(outputs[0].shape) == 2 and outputs[0].shape[1] >= 7:
    boxes = outputs[0]
    boxes = outputs[0]


    # Scale boxes to original image size
    # Scale boxes to original image size
    scale_x = image.width / width
    scale_x = image.width / width
    scale_y = image.height / height
    scale_y = image.height / height


    for box in boxes:
    for box in boxes:
    confidence = box[2]
    confidence = box[2]


    if confidence >= threshold:
    if confidence >= threshold:
    class_id = int(box[1])
    class_id = int(box[1])


    # Get label
    # Get label
    if self.labels and class_id < len(self.labels):
    if self.labels and class_id < len(self.labels):
    label = self.labels[class_id]
    label = self.labels[class_id]
    else:
    else:
    label = f"Class {class_id}"
    label = f"Class {class_id}"


    # Scale coordinates
    # Scale coordinates
    x1 = float(box[3] * scale_x)
    x1 = float(box[3] * scale_x)
    y1 = float(box[4] * scale_y)
    y1 = float(box[4] * scale_y)
    x2 = float(box[5] * scale_x)
    x2 = float(box[5] * scale_x)
    y2 = float(box[6] * scale_y)
    y2 = float(box[6] * scale_y)


    detection = {
    detection = {
    "label": label,
    "label": label,
    "score": float(confidence),
    "score": float(confidence),
    "box": {"x1": x1, "y1": y1, "x2": x2, "y2": y2},
    "box": {"x1": x1, "y1": y1, "x2": x2, "y2": y2},
    }
    }


    detections.append(detection)
    detections.append(detection)


    return detections
    return detections


    def _detect_objects_pytorch(
    def _detect_objects_pytorch(
    self, image: "Image.Image", threshold: float, **kwargs
    self, image: "Image.Image", threshold: float, **kwargs
    ) -> List[Dict[str, Any]]:
    ) -> List[Dict[str, Any]]:
    """
    """
    Detect objects in an image using a PyTorch vision model.
    Detect objects in an image using a PyTorch vision model.


    Args:
    Args:
    image: PIL Image
    image: PIL Image
    threshold: Confidence threshold for detections
    threshold: Confidence threshold for detections
    **kwargs: Additional parameters for object detection
    **kwargs: Additional parameters for object detection


    Returns:
    Returns:
    List of detected objects with bounding boxes and scores
    List of detected objects with bounding boxes and scores
    """
    """
    # Preprocess image
    # Preprocess image
    # Default transformation for common models
    # Default transformation for common models
    transform = transforms.Compose([transforms.ToTensor()])
    transform = transforms.Compose([transforms.ToTensor()])


    # Transform image
    # Transform image
    image_tensor = transform(image).unsqueeze(0).to(self.device)
    image_tensor = transform(image).unsqueeze(0).to(self.device)


    # Run inference
    # Run inference
    with torch.no_grad():
    with torch.no_grad():
    outputs = self.model(image_tensor)
    outputs = self.model(image_tensor)


    # Process outputs
    # Process outputs
    # The format of outputs depends on the specific model
    # The format of outputs depends on the specific model
    # This is a generic implementation that may need to be adapted
    # This is a generic implementation that may need to be adapted


    detections = []
    detections = []


    # Try to handle different output formats
    # Try to handle different output formats
    if (
    if (
    isinstance(outputs, dict)
    isinstance(outputs, dict)
    and "boxes" in outputs
    and "boxes" in outputs
    and "scores" in outputs
    and "scores" in outputs
    and "labels" in outputs
    and "labels" in outputs
    ):
    ):
    # Format used by torchvision detection models
    # Format used by torchvision detection models
    boxes = outputs["boxes"].cpu().numpy()
    boxes = outputs["boxes"].cpu().numpy()
    scores = outputs["scores"].cpu().numpy()
    scores = outputs["scores"].cpu().numpy()
    labels = outputs["labels"].cpu().numpy()
    labels = outputs["labels"].cpu().numpy()


    for box, score, label_id in zip(boxes, scores, labels):
    for box, score, label_id in zip(boxes, scores, labels):
    if score >= threshold:
    if score >= threshold:
    # Get label
    # Get label
    if self.labels and label_id < len(self.labels):
    if self.labels and label_id < len(self.labels):
    label = self.labels[label_id]
    label = self.labels[label_id]
    else:
    else:
    label = f"Class {label_id}"
    label = f"Class {label_id}"


    detection = {
    detection = {
    "label": label,
    "label": label,
    "score": float(score),
    "score": float(score),
    "box": {
    "box": {
    "x1": float(box[0]),
    "x1": float(box[0]),
    "y1": float(box[1]),
    "y1": float(box[1]),
    "x2": float(box[2]),
    "x2": float(box[2]),
    "y2": float(box[3]),
    "y2": float(box[3]),
    },
    },
    }
    }


    detections.append(detection)
    detections.append(detection)


    return detections
    return detections


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
    metadata = {
    metadata = {
    "model_path": self.model_path,
    "model_path": self.model_path,
    "model_type": self.model_type,
    "model_type": self.model_type,
    "model_format": self.model_format,
    "model_format": self.model_format,
    "device": self.device,
    "device": self.device,
    }
    }


    # Add model-specific metadata
    # Add model-specific metadata
    if self.model_format == "huggingface" and self.model:
    if self.model_format == "huggingface" and self.model:
    config = getattr(self.model, "config", None)
    config = getattr(self.model, "config", None)
    if config:
    if config:
    metadata["model_config"] = {
    metadata["model_config"] = {
    "model_type": getattr(config, "model_type", None),
    "model_type": getattr(config, "model_type", None),
    "hidden_size": getattr(config, "hidden_size", None),
    "hidden_size": getattr(config, "hidden_size", None),
    "num_hidden_layers": getattr(config, "num_hidden_layers", None),
    "num_hidden_layers": getattr(config, "num_hidden_layers", None),
    "num_attention_heads": getattr(config, "num_attention_heads", None),
    "num_attention_heads": getattr(config, "num_attention_heads", None),
    }
    }


    return metadata
    return metadata




    # Example usage
    # Example usage
    if __name__ == "__main__":
    if __name__ == "__main__":
    # Example model path (replace with an actual model path)
    # Example model path (replace with an actual model path)
    model_path = "path/to/model"
    model_path = "path/to/model"


    if os.path.exists(model_path):
    if os.path.exists(model_path):
    # Create vision model
    # Create vision model
    model = VisionModel(model_path=model_path, model_type="image-classification")
    model = VisionModel(model_path=model_path, model_type="image-classification")


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


    # Classify an image
    # Classify an image
    image_path = "path/to/image.jpg"
    image_path = "path/to/image.jpg"
    if os.path.exists(image_path):
    if os.path.exists(image_path):
    print(f"\nClassifying image: {image_path}")
    print(f"\nClassifying image: {image_path}")
    results = model.classify_image(image_path)
    results = model.classify_image(image_path)


    # Print top 5 results
    # Print top 5 results
    print("Top 5 results:")
    print("Top 5 results:")
    for label, score in sorted(
    for label, score in sorted(
    results.items(), key=lambda x: x[1], reverse=True
    results.items(), key=lambda x: x[1], reverse=True
    )[:5]:
    )[:5]:
    print(f"  {label}: {score:.4f}")
    print(f"  {label}: {score:.4f}")
    else:
    else:
    print(f"Model file not found: {model_path}")
    print(f"Model file not found: {model_path}")
    print("Please specify a valid model path.")
    print("Please specify a valid model path.")