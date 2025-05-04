"""
"""
Audio model implementation for the AI Models module.
Audio model implementation for the AI Models module.


This module provides specialized classes for working with audio models,
This module provides specialized classes for working with audio models,
including speech recognition, text-to-speech, and audio classification.
including speech recognition, text-to-speech, and audio classification.
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
    from typing import Any, Dict, List, Optional, Tuple
    from typing import Any, Dict, List, Optional, Tuple


    import numpy as np
    import numpy as np
    import torch
    import torch
    import transformers
    import transformers
    from transformers import AutoProcessor
    from transformers import AutoProcessor


    TRANSFORMERS_AVAILABLE
    TRANSFORMERS_AVAILABLE
    import librosa
    import librosa
    import onnxruntime
    import onnxruntime
    import soundfile
    import soundfile
    from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor
    from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor


    self.processor
    self.processor
    from transformers import (AutoModelForTextToSpeech,
    from transformers import (AutoModelForTextToSpeech,
    AutoProcessor)
    AutoProcessor)


    self.processor
    self.processor
    from transformers import AutoProcessor
    from transformers import AutoProcessor


    self.processor
    self.processor
    from transformers import AutoProcessor
    from transformers import AutoProcessor


    self.processor
    self.processor
    from transformers import AutoFeatureExtractor
    from transformers import AutoFeatureExtractor


    self.processor
    self.processor
    from transformers import Wav2Vec2ForCTC
    from transformers import Wav2Vec2ForCTC


    self.model
    self.model
    from transformers import \
    from transformers import \
    WhisperForConditionalGeneration
    WhisperForConditionalGeneration


    self.model
    self.model
    from transformers import AutoProcessor
    from transformers import AutoProcessor


    self.processor
    self.processor
    from transformers import AutoProcessor
    from transformers import AutoProcessor


    self.processor
    self.processor
    from transformers import AutoFeatureExtractor
    from transformers import AutoFeatureExtractor


    self.processor
    self.processor
    from scipy.io import wavfile
    from scipy.io import wavfile


    wavfile.write
    wavfile.write
    from scipy.io import wavfile
    from scipy.io import wavfile


    wavfile.write
    wavfile.write
    from scipy.io import wavfile
    from scipy.io import wavfile


    wavfile.write
    wavfile.write


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
    logger.warning("PyTorch not available. Audio model support will be limited.")
    logger.warning("PyTorch not available. Audio model support will be limited.")
    TORCH_AVAILABLE = False
    TORCH_AVAILABLE = False


    try:
    try:


    = True
    = True
except ImportError:
except ImportError:
    logger.warning("Transformers not available. Audio model support will be limited.")
    logger.warning("Transformers not available. Audio model support will be limited.")
    TRANSFORMERS_AVAILABLE = False
    TRANSFORMERS_AVAILABLE = False


    try:
    try:




    LIBROSA_AVAILABLE = True
    LIBROSA_AVAILABLE = True
except ImportError:
except ImportError:
    logger.warning("Librosa not available. Audio preprocessing will be limited.")
    logger.warning("Librosa not available. Audio preprocessing will be limited.")
    LIBROSA_AVAILABLE = False
    LIBROSA_AVAILABLE = False


    try:
    try:
    as sf
    as sf


    SOUNDFILE_AVAILABLE = True
    SOUNDFILE_AVAILABLE = True
except ImportError:
except ImportError:
    logger.warning("SoundFile not available. Audio file handling will be limited.")
    logger.warning("SoundFile not available. Audio file handling will be limited.")
    SOUNDFILE_AVAILABLE = False
    SOUNDFILE_AVAILABLE = False


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
    "ONNX Runtime not available. ONNX audio model support will be limited."
    "ONNX Runtime not available. ONNX audio model support will be limited."
    )
    )
    ONNX_AVAILABLE = False
    ONNX_AVAILABLE = False




    class AudioModel:
    class AudioModel:
    """
    """
    Base class for audio models.
    Base class for audio models.
    """
    """


    def __init__(
    def __init__(
    self,
    self,
    model_path: str,
    model_path: str,
    model_type: str = "speech-recognition",
    model_type: str = "speech-recognition",
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
    Initialize an audio model.
    Initialize an audio model.


    Args:
    Args:
    model_path: Path to the model file or directory
    model_path: Path to the model file or directory
    model_type: Type of model (speech-recognition, text-to-speech, audio-classification)
    model_type: Type of model (speech-recognition, text-to-speech, audio-classification)
    processor_path: Optional path to the audio processor
    processor_path: Optional path to the audio processor
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


    logger.info(f"Initializing audio model: {model_path}")
    logger.info(f"Initializing audio model: {model_path}")
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
    Load the audio model.
    Load the audio model.
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
    Load a Hugging Face audio model.
    Load a Hugging Face audio model.
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


    logger.info(f"Loading Hugging Face audio model: {self.model_path}")
    logger.info(f"Loading Hugging Face audio model: {self.model_path}")


    try:
    try:
    # Load processor and model based on model type
    # Load processor and model based on model type
    if self.model_type == "speech-recognition":
    if self.model_type == "speech-recognition":
    = AutoProcessor.from_pretrained(self.processor_path)
    = AutoProcessor.from_pretrained(self.processor_path)
    self.model = AutoModelForSpeechSeq2Seq.from_pretrained(
    self.model = AutoModelForSpeechSeq2Seq.from_pretrained(
    self.model_path, **self.kwargs
    self.model_path, **self.kwargs
    )
    )


    elif self.model_type == "text-to-speech":
    elif self.model_type == "text-to-speech":
    = AutoProcessor.from_pretrained(self.processor_path)
    = AutoProcessor.from_pretrained(self.processor_path)
    self.model = AutoModelForTextToSpeech.from_pretrained(
    self.model = AutoModelForTextToSpeech.from_pretrained(
    self.model_path, **self.kwargs
    self.model_path, **self.kwargs
    )
    )


    elif self.model_type == "audio-classification":
    elif self.model_type == "audio-classification":
    from transformers import (AutoFeatureExtractor,
    from transformers import (AutoFeatureExtractor,
    AutoModelForAudioClassification)
    AutoModelForAudioClassification)


    self.processor = AutoFeatureExtractor.from_pretrained(
    self.processor = AutoFeatureExtractor.from_pretrained(
    self.processor_path
    self.processor_path
    )
    )
    self.model = AutoModelForAudioClassification.from_pretrained(
    self.model = AutoModelForAudioClassification.from_pretrained(
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
    f"Successfully loaded Hugging Face audio model: {self.model_path}"
    f"Successfully loaded Hugging Face audio model: {self.model_path}"
    )
    )


except Exception as e:
except Exception as e:
    logger.error(f"Error loading Hugging Face audio model: {e}")
    logger.error(f"Error loading Hugging Face audio model: {e}")
    raise
    raise


    def _load_onnx_model(self) -> None:
    def _load_onnx_model(self) -> None:
    """
    """
    Load an ONNX audio model.
    Load an ONNX audio model.
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


    logger.info(f"Loading ONNX audio model: {self.model_path}")
    logger.info(f"Loading ONNX audio model: {self.model_path}")


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


    logger.info(f"Successfully loaded ONNX audio model: {self.model_path}")
    logger.info(f"Successfully loaded ONNX audio model: {self.model_path}")
    logger.info(f"Model inputs: {self.input_names}")
    logger.info(f"Model inputs: {self.input_names}")
    logger.info(f"Model outputs: {self.output_names}")
    logger.info(f"Model outputs: {self.output_names}")


    # Try to load processor if available
    # Try to load processor if available
    self._load_processor_for_onnx()
    self._load_processor_for_onnx()


except Exception as e:
except Exception as e:
    logger.error(f"Error loading ONNX audio model: {e}")
    logger.error(f"Error loading ONNX audio model: {e}")
    raise
    raise


    def _load_processor_for_onnx(self) -> None:
    def _load_processor_for_onnx(self) -> None:
    """
    """
    Load a processor for an ONNX model.
    Load a processor for an ONNX model.
    """
    """
    if not TRANSFORMERS_AVAILABLE:
    if not TRANSFORMERS_AVAILABLE:
    logger.warning(
    logger.warning(
    "Transformers not available. Cannot load processor for ONNX model."
    "Transformers not available. Cannot load processor for ONNX model."
    )
    )
    return try:
    return try:
    # Try to load processor from processor_path
    # Try to load processor from processor_path
    if self.processor_path and os.path.exists(self.processor_path):
    if self.processor_path and os.path.exists(self.processor_path):
    if self.model_type == "speech-recognition":
    if self.model_type == "speech-recognition":
    = AutoProcessor.from_pretrained(self.processor_path)
    = AutoProcessor.from_pretrained(self.processor_path)


    elif self.model_type == "text-to-speech":
    elif self.model_type == "text-to-speech":
    = AutoProcessor.from_pretrained(self.processor_path)
    = AutoProcessor.from_pretrained(self.processor_path)


    elif self.model_type == "audio-classification":
    elif self.model_type == "audio-classification":
    = AutoFeatureExtractor.from_pretrained(
    = AutoFeatureExtractor.from_pretrained(
    self.processor_path
    self.processor_path
    )
    )


    logger.info(f"Loaded processor from {self.processor_path}")
    logger.info(f"Loaded processor from {self.processor_path}")
    else:
    else:
    logger.warning("No processor path specified or path does not exist.")
    logger.warning("No processor path specified or path does not exist.")


except Exception as e:
except Exception as e:
    logger.warning(f"Error loading processor for ONNX model: {e}")
    logger.warning(f"Error loading processor for ONNX model: {e}")


    def _load_pytorch_model(self) -> None:
    def _load_pytorch_model(self) -> None:
    """
    """
    Load a PyTorch audio model.
    Load a PyTorch audio model.
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


    logger.info(f"Loading PyTorch audio model: {self.model_path}")
    logger.info(f"Loading PyTorch audio model: {self.model_path}")


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
    if model_type == "wav2vec2":
    if model_type == "wav2vec2":
    = Wav2Vec2ForCTC.from_pretrained(
    = Wav2Vec2ForCTC.from_pretrained(
    "facebook/wav2vec2-base-960h"
    "facebook/wav2vec2-base-960h"
    )
    )
    elif model_type == "whisper":
    elif model_type == "whisper":
    = WhisperForConditionalGeneration.from_pretrained(
    = WhisperForConditionalGeneration.from_pretrained(
    "openai/whisper-small"
    "openai/whisper-small"
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


    logger.info(f"Successfully loaded PyTorch audio model: {self.model_path}")
    logger.info(f"Successfully loaded PyTorch audio model: {self.model_path}")


    # Try to load processor if available
    # Try to load processor if available
    self._load_processor_for_pytorch()
    self._load_processor_for_pytorch()


except Exception as e:
except Exception as e:
    logger.error(f"Error loading PyTorch audio model: {e}")
    logger.error(f"Error loading PyTorch audio model: {e}")
    raise
    raise


    def _load_processor_for_pytorch(self) -> None:
    def _load_processor_for_pytorch(self) -> None:
    """
    """
    Load a processor for a PyTorch model.
    Load a processor for a PyTorch model.
    """
    """
    if not TRANSFORMERS_AVAILABLE:
    if not TRANSFORMERS_AVAILABLE:
    logger.warning(
    logger.warning(
    "Transformers not available. Cannot load processor for PyTorch model."
    "Transformers not available. Cannot load processor for PyTorch model."
    )
    )
    return try:
    return try:
    # Try to load processor from processor_path
    # Try to load processor from processor_path
    if self.processor_path and os.path.exists(self.processor_path):
    if self.processor_path and os.path.exists(self.processor_path):
    if self.model_type == "speech-recognition":
    if self.model_type == "speech-recognition":
    = AutoProcessor.from_pretrained(self.processor_path)
    = AutoProcessor.from_pretrained(self.processor_path)


    elif self.model_type == "text-to-speech":
    elif self.model_type == "text-to-speech":
    = AutoProcessor.from_pretrained(self.processor_path)
    = AutoProcessor.from_pretrained(self.processor_path)


    elif self.model_type == "audio-classification":
    elif self.model_type == "audio-classification":
    = AutoFeatureExtractor.from_pretrained(
    = AutoFeatureExtractor.from_pretrained(
    self.processor_path
    self.processor_path
    )
    )


    logger.info(f"Loaded processor from {self.processor_path}")
    logger.info(f"Loaded processor from {self.processor_path}")
    else:
    else:
    logger.warning("No processor path specified or path does not exist.")
    logger.warning("No processor path specified or path does not exist.")


except Exception as e:
except Exception as e:
    logger.warning(f"Error loading processor for PyTorch model: {e}")
    logger.warning(f"Error loading processor for PyTorch model: {e}")


    def _load_audio(self, audio_path: str) -> Tuple[np.ndarray, int]:
    def _load_audio(self, audio_path: str) -> Tuple[np.ndarray, int]:
    """
    """
    Load an audio file.
    Load an audio file.


    Args:
    Args:
    audio_path: Path to the audio file
    audio_path: Path to the audio file


    Returns:
    Returns:
    Tuple of (audio_array, sample_rate)
    Tuple of (audio_array, sample_rate)
    """
    """
    if not LIBROSA_AVAILABLE:
    if not LIBROSA_AVAILABLE:
    raise ImportError(
    raise ImportError(
    "Librosa not available. Please install it with: pip install librosa"
    "Librosa not available. Please install it with: pip install librosa"
    )
    )


    try:
    try:
    # Load audio file
    # Load audio file
    audio_array, sample_rate = librosa.load(audio_path, sr=None)
    audio_array, sample_rate = librosa.load(audio_path, sr=None)


    return audio_array, sample_rate
    return audio_array, sample_rate


except Exception as e:
except Exception as e:
    logger.error(f"Error loading audio file: {e}")
    logger.error(f"Error loading audio file: {e}")
    raise
    raise


    def transcribe(
    def transcribe(
    self, audio_path: str, language: Optional[str] = None, **kwargs
    self, audio_path: str, language: Optional[str] = None, **kwargs
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Transcribe speech from an audio file.
    Transcribe speech from an audio file.


    Args:
    Args:
    audio_path: Path to the audio file
    audio_path: Path to the audio file
    language: Optional language code (e.g., "en", "fr", "de")
    language: Optional language code (e.g., "en", "fr", "de")
    **kwargs: Additional parameters for transcription
    **kwargs: Additional parameters for transcription


    Returns:
    Returns:
    Dictionary with transcription results
    Dictionary with transcription results
    """
    """
    if not self.model:
    if not self.model:
    self.load()
    self.load()


    if self.model_type != "speech-recognition":
    if self.model_type != "speech-recognition":
    raise ValueError(
    raise ValueError(
    f"Model type {self.model_type} does not support speech recognition"
    f"Model type {self.model_type} does not support speech recognition"
    )
    )


    try:
    try:
    # Load audio
    # Load audio
    audio_array, sample_rate = self._load_audio(audio_path)
    audio_array, sample_rate = self._load_audio(audio_path)


    if self.model_format == "huggingface":
    if self.model_format == "huggingface":
    return self._transcribe_huggingface(
    return self._transcribe_huggingface(
    audio_array, sample_rate, language, **kwargs
    audio_array, sample_rate, language, **kwargs
    )
    )
    elif self.model_format == "onnx":
    elif self.model_format == "onnx":
    return self._transcribe_onnx(
    return self._transcribe_onnx(
    audio_array, sample_rate, language, **kwargs
    audio_array, sample_rate, language, **kwargs
    )
    )
    elif self.model_format == "pytorch":
    elif self.model_format == "pytorch":
    return self._transcribe_pytorch(
    return self._transcribe_pytorch(
    audio_array, sample_rate, language, **kwargs
    audio_array, sample_rate, language, **kwargs
    )
    )
    else:
    else:
    raise ValueError(f"Unsupported model format: {self.model_format}")
    raise ValueError(f"Unsupported model format: {self.model_format}")


except Exception as e:
except Exception as e:
    logger.error(f"Error transcribing audio: {e}")
    logger.error(f"Error transcribing audio: {e}")
    raise
    raise


    def _transcribe_huggingface(
    def _transcribe_huggingface(
    self,
    self,
    audio_array: np.ndarray,
    audio_array: np.ndarray,
    sample_rate: int,
    sample_rate: int,
    language: Optional[str] = None,
    language: Optional[str] = None,
    **kwargs,
    **kwargs,
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Transcribe speech using a Hugging Face model.
    Transcribe speech using a Hugging Face model.


    Args:
    Args:
    audio_array: Audio data as numpy array
    audio_array: Audio data as numpy array
    sample_rate: Sample rate of the audio
    sample_rate: Sample rate of the audio
    language: Optional language code
    language: Optional language code
    **kwargs: Additional parameters for transcription
    **kwargs: Additional parameters for transcription


    Returns:
    Returns:
    Dictionary with transcription results
    Dictionary with transcription results
    """
    """
    try:
    try:
    # Check if we need to resample
    # Check if we need to resample
    model_sample_rate = getattr(
    model_sample_rate = getattr(
    self.processor.feature_extractor, "sampling_rate", 16000
    self.processor.feature_extractor, "sampling_rate", 16000
    )
    )
    if sample_rate != model_sample_rate:
    if sample_rate != model_sample_rate:
    if LIBROSA_AVAILABLE:
    if LIBROSA_AVAILABLE:
    logger.info(
    logger.info(
    f"Resampling audio from {sample_rate} Hz to {model_sample_rate} Hz"
    f"Resampling audio from {sample_rate} Hz to {model_sample_rate} Hz"
    )
    )
    audio_array = librosa.resample(
    audio_array = librosa.resample(
    audio_array, orig_sr=sample_rate, target_sr=model_sample_rate
    audio_array, orig_sr=sample_rate, target_sr=model_sample_rate
    )
    )
    sample_rate = model_sample_rate
    sample_rate = model_sample_rate
    else:
    else:
    logger.warning(
    logger.warning(
    f"Audio sample rate ({sample_rate} Hz) doesn't match model sample rate ({model_sample_rate} Hz), but librosa is not available for resampling"
    f"Audio sample rate ({sample_rate} Hz) doesn't match model sample rate ({model_sample_rate} Hz), but librosa is not available for resampling"
    )
    )


    # Process audio
    # Process audio
    inputs = self.processor(
    inputs = self.processor(
    audio_array, sampling_rate=sample_rate, return_tensors="pt"
    audio_array, sampling_rate=sample_rate, return_tensors="pt"
    ).to(self.device)
    ).to(self.device)


    # Add language information if provided and supported
    # Add language information if provided and supported
    generation_kwargs = {}
    generation_kwargs = {}
    if (
    if (
    language
    language
    and hasattr(self.processor, "tokenizer")
    and hasattr(self.processor, "tokenizer")
    and hasattr(self.processor.tokenizer, "language_codes")
    and hasattr(self.processor.tokenizer, "language_codes")
    ):
    ):
    if language in self.processor.tokenizer.language_codes:
    if language in self.processor.tokenizer.language_codes:
    forced_decoder_ids = (
    forced_decoder_ids = (
    self.processor.tokenizer.get_decoder_prompt_ids(
    self.processor.tokenizer.get_decoder_prompt_ids(
    language=language
    language=language
    )
    )
    )
    )
    generation_kwargs["forced_decoder_ids"] = forced_decoder_ids
    generation_kwargs["forced_decoder_ids"] = forced_decoder_ids
    else:
    else:
    logger.warning(f"Language {language} not supported by the model")
    logger.warning(f"Language {language} not supported by the model")


    # Add any additional kwargs
    # Add any additional kwargs
    generation_kwargs.update(kwargs)
    generation_kwargs.update(kwargs)


    # Generate transcription
    # Generate transcription
    with torch.no_grad():
    with torch.no_grad():
    outputs = self.model.generate(
    outputs = self.model.generate(
    inputs.input_features, **generation_kwargs
    inputs.input_features, **generation_kwargs
    )
    )


    # Decode output
    # Decode output
    transcription = self.processor.batch_decode(
    transcription = self.processor.batch_decode(
    outputs, skip_special_tokens=True
    outputs, skip_special_tokens=True
    )[0]
    )[0]


    # Create result
    # Create result
    result = {"text": transcription, "language": language}
    result = {"text": transcription, "language": language}


    return result
    return result


except Exception as e:
except Exception as e:
    logger.error(f"Error transcribing with Hugging Face model: {e}")
    logger.error(f"Error transcribing with Hugging Face model: {e}")
    raise
    raise


    def _transcribe_onnx(
    def _transcribe_onnx(
    self,
    self,
    audio_array: np.ndarray,
    audio_array: np.ndarray,
    sample_rate: int,
    sample_rate: int,
    language: Optional[str] = None,
    language: Optional[str] = None,
    **kwargs,
    **kwargs,
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Transcribe speech using an ONNX model.
    Transcribe speech using an ONNX model.


    Args:
    Args:
    audio_array: Audio data as numpy array
    audio_array: Audio data as numpy array
    sample_rate: Sample rate of the audio
    sample_rate: Sample rate of the audio
    language: Optional language code
    language: Optional language code
    **kwargs: Additional parameters for transcription
    **kwargs: Additional parameters for transcription


    Returns:
    Returns:
    Dictionary with transcription results
    Dictionary with transcription results
    """
    """
    try:
    try:
    # This is a simplified implementation and may need to be adapted for specific models
    # This is a simplified implementation and may need to be adapted for specific models


    # Check if we have a processor
    # Check if we have a processor
    if self.processor:
    if self.processor:
    # Use the processor to prepare inputs
    # Use the processor to prepare inputs
    inputs = self.processor(
    inputs = self.processor(
    audio_array, sampling_rate=sample_rate, return_tensors="np"
    audio_array, sampling_rate=sample_rate, return_tensors="np"
    )
    )


    # Extract the input features
    # Extract the input features
    if "input_features" in inputs:
    if "input_features" in inputs:
    input_data = inputs.input_features
    input_data = inputs.input_features
    else:
    else:
    # Use the first input as fallback
    # Use the first input as fallback
    input_data = list(inputs.values())[0]
    input_data = list(inputs.values())[0]
    else:
    else:
    # Basic preprocessing without a processor
    # Basic preprocessing without a processor
    # Resample if needed (assuming 16kHz is common for speech models)
    # Resample if needed (assuming 16kHz is common for speech models)
    if sample_rate != 16000:
    if sample_rate != 16000:
    if LIBROSA_AVAILABLE:
    if LIBROSA_AVAILABLE:
    logger.info(
    logger.info(
    f"Resampling audio from {sample_rate} Hz to 16000 Hz"
    f"Resampling audio from {sample_rate} Hz to 16000 Hz"
    )
    )
    audio_array = librosa.resample(
    audio_array = librosa.resample(
    audio_array, orig_sr=sample_rate, target_sr=16000
    audio_array, orig_sr=sample_rate, target_sr=16000
    )
    )
    else:
    else:
    logger.warning(
    logger.warning(
    "Audio sample rate doesn't match 16000 Hz, but librosa is not available for resampling"
    "Audio sample rate doesn't match 16000 Hz, but librosa is not available for resampling"
    )
    )


    # Convert to float32 and normalize
    # Convert to float32 and normalize
    input_data = audio_array.astype(np.float32)
    input_data = audio_array.astype(np.float32)


    # Add batch dimension if needed
    # Add batch dimension if needed
    if input_data.ndim == 1:
    if input_data.ndim == 1:
    input_data = np.expand_dims(input_data, axis=0)
    input_data = np.expand_dims(input_data, axis=0)


    # Prepare ONNX inputs
    # Prepare ONNX inputs
    onnx_inputs = {}
    onnx_inputs = {}


    # Map inputs based on model's expected input names
    # Map inputs based on model's expected input names
    if len(self.input_names) == 1:
    if len(self.input_names) == 1:
    # If there's only one input, use it directly
    # If there's only one input, use it directly
    onnx_inputs[self.input_names[0]] = input_data
    onnx_inputs[self.input_names[0]] = input_data
    else:
    else:
    # Try to map to common input names
    # Try to map to common input names
    if "input_features" in self.input_names:
    if "input_features" in self.input_names:
    onnx_inputs["input_features"] = input_data
    onnx_inputs["input_features"] = input_data
    elif "input" in self.input_names:
    elif "input" in self.input_names:
    onnx_inputs["input"] = input_data
    onnx_inputs["input"] = input_data
    else:
    else:
    # Use the first input name
    # Use the first input name
    onnx_inputs[self.input_names[0]] = input_data
    onnx_inputs[self.input_names[0]] = input_data


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


    # Try to decode the output if we have a processor
    # Try to decode the output if we have a processor
    if self.processor and hasattr(self.processor, "batch_decode"):
    if self.processor and hasattr(self.processor, "batch_decode"):
    transcription = self.processor.batch_decode(
    transcription = self.processor.batch_decode(
    outputs[0], skip_special_tokens=True
    outputs[0], skip_special_tokens=True
    )[0]
    )[0]
    else:
    else:
    # Return raw output as string
    # Return raw output as string
    transcription = str(outputs)
    transcription = str(outputs)


    # Create result
    # Create result
    result = {"text": transcription, "language": language}
    result = {"text": transcription, "language": language}


    return result
    return result


except Exception as e:
except Exception as e:
    logger.error(f"Error transcribing with ONNX model: {e}")
    logger.error(f"Error transcribing with ONNX model: {e}")
    raise
    raise


    def _transcribe_pytorch(
    def _transcribe_pytorch(
    self,
    self,
    audio_array: np.ndarray,
    audio_array: np.ndarray,
    sample_rate: int,
    sample_rate: int,
    language: Optional[str] = None,
    language: Optional[str] = None,
    **kwargs,
    **kwargs,
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Transcribe speech using a PyTorch model.
    Transcribe speech using a PyTorch model.


    Args:
    Args:
    audio_array: Audio data as numpy array
    audio_array: Audio data as numpy array
    sample_rate: Sample rate of the audio
    sample_rate: Sample rate of the audio
    language: Optional language code
    language: Optional language code
    **kwargs: Additional parameters for transcription
    **kwargs: Additional parameters for transcription


    Returns:
    Returns:
    Dictionary with transcription results
    Dictionary with transcription results
    """
    """
    try:
    try:
    # Check if we have a processor
    # Check if we have a processor
    if self.processor:
    if self.processor:
    # Use the processor to prepare inputs
    # Use the processor to prepare inputs
    inputs = self.processor(
    inputs = self.processor(
    audio_array, sampling_rate=sample_rate, return_tensors="pt"
    audio_array, sampling_rate=sample_rate, return_tensors="pt"
    ).to(self.device)
    ).to(self.device)


    # Generate transcription
    # Generate transcription
    with torch.no_grad():
    with torch.no_grad():
    if hasattr(self.model, "generate"):
    if hasattr(self.model, "generate"):
    # Add language information if provided and supported
    # Add language information if provided and supported
    generation_kwargs = {}
    generation_kwargs = {}
    if (
    if (
    language
    language
    and hasattr(self.processor, "tokenizer")
    and hasattr(self.processor, "tokenizer")
    and hasattr(self.processor.tokenizer, "language_codes")
    and hasattr(self.processor.tokenizer, "language_codes")
    ):
    ):
    if language in self.processor.tokenizer.language_codes:
    if language in self.processor.tokenizer.language_codes:
    forced_decoder_ids = (
    forced_decoder_ids = (
    self.processor.tokenizer.get_decoder_prompt_ids(
    self.processor.tokenizer.get_decoder_prompt_ids(
    language=language
    language=language
    )
    )
    )
    )
    generation_kwargs["forced_decoder_ids"] = (
    generation_kwargs["forced_decoder_ids"] = (
    forced_decoder_ids
    forced_decoder_ids
    )
    )
    else:
    else:
    logger.warning(
    logger.warning(
    f"Language {language} not supported by the model"
    f"Language {language} not supported by the model"
    )
    )


    # Add any additional kwargs
    # Add any additional kwargs
    generation_kwargs.update(kwargs)
    generation_kwargs.update(kwargs)


    # Generate
    # Generate
    if "input_features" in inputs:
    if "input_features" in inputs:
    outputs = self.model.generate(
    outputs = self.model.generate(
    inputs.input_features, **generation_kwargs
    inputs.input_features, **generation_kwargs
    )
    )
    else:
    else:
    outputs = self.model.generate(**inputs, **generation_kwargs)
    outputs = self.model.generate(**inputs, **generation_kwargs)


    # Decode output
    # Decode output
    transcription = self.processor.batch_decode(
    transcription = self.processor.batch_decode(
    outputs, skip_special_tokens=True
    outputs, skip_special_tokens=True
    )[0]
    )[0]
    else:
    else:
    # For models that don't have generate method
    # For models that don't have generate method
    outputs = self.model(**inputs)
    outputs = self.model(**inputs)


    if hasattr(outputs, "logits"):
    if hasattr(outputs, "logits"):
    # Get predictions
    # Get predictions
    predictions = torch.argmax(outputs.logits, dim=-1)
    predictions = torch.argmax(outputs.logits, dim=-1)


    # Decode output
    # Decode output
    if hasattr(self.processor, "batch_decode"):
    if hasattr(self.processor, "batch_decode"):
    transcription = self.processor.batch_decode(
    transcription = self.processor.batch_decode(
    predictions
    predictions
    )[0]
    )[0]
    else:
    else:
    transcription = str(predictions.cpu().numpy())
    transcription = str(predictions.cpu().numpy())
    else:
    else:
    transcription = str(outputs)
    transcription = str(outputs)
    else:
    else:
    # Basic inference without a processor
    # Basic inference without a processor
    # Convert to tensor
    # Convert to tensor
    audio_tensor = (
    audio_tensor = (
    torch.tensor(audio_array, dtype=torch.float32)
    torch.tensor(audio_array, dtype=torch.float32)
    .unsqueeze(0)
    .unsqueeze(0)
    .to(self.device)
    .to(self.device)
    )
    )


    # Run inference
    # Run inference
    with torch.no_grad():
    with torch.no_grad():
    outputs = self.model(audio_tensor)
    outputs = self.model(audio_tensor)


    # Return raw output as string
    # Return raw output as string
    transcription = str(outputs)
    transcription = str(outputs)


    # Create result
    # Create result
    result = {"text": transcription, "language": language}
    result = {"text": transcription, "language": language}


    return result
    return result


except Exception as e:
except Exception as e:
    logger.error(f"Error transcribing with PyTorch model: {e}")
    logger.error(f"Error transcribing with PyTorch model: {e}")
    raise
    raise


    def synthesize_speech(
    def synthesize_speech(
    self,
    self,
    text: str,
    text: str,
    output_path: str,
    output_path: str,
    voice_id: Optional[str] = None,
    voice_id: Optional[str] = None,
    language: Optional[str] = None,
    language: Optional[str] = None,
    **kwargs,
    **kwargs,
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Synthesize speech from text.
    Synthesize speech from text.


    Args:
    Args:
    text: Text to synthesize
    text: Text to synthesize
    output_path: Path to save the audio file
    output_path: Path to save the audio file
    voice_id: Optional voice ID or speaker ID
    voice_id: Optional voice ID or speaker ID
    language: Optional language code
    language: Optional language code
    **kwargs: Additional parameters for synthesis
    **kwargs: Additional parameters for synthesis


    Returns:
    Returns:
    Dictionary with synthesis results
    Dictionary with synthesis results
    """
    """
    if not self.model:
    if not self.model:
    self.load()
    self.load()


    if self.model_type != "text-to-speech":
    if self.model_type != "text-to-speech":
    raise ValueError(
    raise ValueError(
    f"Model type {self.model_type} does not support text-to-speech"
    f"Model type {self.model_type} does not support text-to-speech"
    )
    )


    try:
    try:
    if self.model_format == "huggingface":
    if self.model_format == "huggingface":
    return self._synthesize_speech_huggingface(
    return self._synthesize_speech_huggingface(
    text, output_path, voice_id, language, **kwargs
    text, output_path, voice_id, language, **kwargs
    )
    )
    elif self.model_format == "onnx":
    elif self.model_format == "onnx":
    return self._synthesize_speech_onnx(
    return self._synthesize_speech_onnx(
    text, output_path, voice_id, language, **kwargs
    text, output_path, voice_id, language, **kwargs
    )
    )
    elif self.model_format == "pytorch":
    elif self.model_format == "pytorch":
    return self._synthesize_speech_pytorch(
    return self._synthesize_speech_pytorch(
    text, output_path, voice_id, language, **kwargs
    text, output_path, voice_id, language, **kwargs
    )
    )
    else:
    else:
    raise ValueError(f"Unsupported model format: {self.model_format}")
    raise ValueError(f"Unsupported model format: {self.model_format}")


except Exception as e:
except Exception as e:
    logger.error(f"Error synthesizing speech: {e}")
    logger.error(f"Error synthesizing speech: {e}")
    raise
    raise


    def _synthesize_speech_huggingface(
    def _synthesize_speech_huggingface(
    self,
    self,
    text: str,
    text: str,
    output_path: str,
    output_path: str,
    voice_id: Optional[str] = None,
    voice_id: Optional[str] = None,
    language: Optional[str] = None,
    language: Optional[str] = None,
    **kwargs,
    **kwargs,
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Synthesize speech using a Hugging Face model.
    Synthesize speech using a Hugging Face model.


    Args:
    Args:
    text: Text to synthesize
    text: Text to synthesize
    output_path: Path to save the audio file
    output_path: Path to save the audio file
    voice_id: Optional voice ID or speaker ID
    voice_id: Optional voice ID or speaker ID
    language: Optional language code
    language: Optional language code
    **kwargs: Additional parameters for synthesis
    **kwargs: Additional parameters for synthesis


    Returns:
    Returns:
    Dictionary with synthesis results
    Dictionary with synthesis results
    """
    """
    try:
    try:
    # Process text
    # Process text
    inputs = self.processor(text=text, return_tensors="pt").to(self.device)
    inputs = self.processor(text=text, return_tensors="pt").to(self.device)


    # Add speaker embedding if voice_id is provided
    # Add speaker embedding if voice_id is provided
    if voice_id and hasattr(self.processor, "speakers"):
    if voice_id and hasattr(self.processor, "speakers"):
    if voice_id in self.processor.speakers:
    if voice_id in self.processor.speakers:
    speaker_embeddings = self.processor.speakers[voice_id]
    speaker_embeddings = self.processor.speakers[voice_id]
    speaker_embeddings = (
    speaker_embeddings = (
    torch.tensor(speaker_embeddings).unsqueeze(0).to(self.device)
    torch.tensor(speaker_embeddings).unsqueeze(0).to(self.device)
    )
    )
    inputs["speaker_embeddings"] = speaker_embeddings
    inputs["speaker_embeddings"] = speaker_embeddings
    else:
    else:
    logger.warning(f"Voice ID {voice_id} not found in available voices")
    logger.warning(f"Voice ID {voice_id} not found in available voices")


    # Add language information if provided
    # Add language information if provided
    if language and hasattr(self.processor, "languages"):
    if language and hasattr(self.processor, "languages"):
    if language in self.processor.languages:
    if language in self.processor.languages:
    inputs["language"] = language
    inputs["language"] = language
    else:
    else:
    logger.warning(f"Language {language} not supported by the model")
    logger.warning(f"Language {language} not supported by the model")


    # Generate speech
    # Generate speech
    with torch.no_grad():
    with torch.no_grad():
    outputs = self.model(**inputs)
    outputs = self.model(**inputs)


    # Get waveform
    # Get waveform
    if hasattr(outputs, "waveform"):
    if hasattr(outputs, "waveform"):
    waveform = outputs.waveform.cpu().numpy()[0]
    waveform = outputs.waveform.cpu().numpy()[0]
    elif hasattr(outputs, "audio"):
    elif hasattr(outputs, "audio"):
    waveform = outputs.audio.cpu().numpy()[0]
    waveform = outputs.audio.cpu().numpy()[0]
    else:
    else:
    # Try to get the first output
    # Try to get the first output
    waveform = list(outputs.values())[0].cpu().numpy()[0]
    waveform = list(outputs.values())[0].cpu().numpy()[0]


    # Get sample rate
    # Get sample rate
    sample_rate = getattr(self.processor, "sampling_rate", 16000)
    sample_rate = getattr(self.processor, "sampling_rate", 16000)


    # Save audio file
    # Save audio file
    if SOUNDFILE_AVAILABLE:
    if SOUNDFILE_AVAILABLE:
    sf.write(output_path, waveform, sample_rate)
    sf.write(output_path, waveform, sample_rate)
    else:
    else:
    # Try to use scipy as fallback
    # Try to use scipy as fallback
    try:
    try:
    (output_path, sample_rate, waveform)
    (output_path, sample_rate, waveform)
except ImportError:
except ImportError:
    raise ImportError(
    raise ImportError(
    "Neither SoundFile nor scipy.io.wavfile is available. Please install one of them."
    "Neither SoundFile nor scipy.io.wavfile is available. Please install one of them."
    )
    )


    # Create result
    # Create result
    result = {
    result = {
    "text": text,
    "text": text,
    "output_path": output_path,
    "output_path": output_path,
    "sample_rate": sample_rate,
    "sample_rate": sample_rate,
    "duration": len(waveform) / sample_rate,
    "duration": len(waveform) / sample_rate,
    "voice_id": voice_id,
    "voice_id": voice_id,
    "language": language,
    "language": language,
    }
    }


    return result
    return result


except Exception as e:
except Exception as e:
    logger.error(f"Error synthesizing speech with Hugging Face model: {e}")
    logger.error(f"Error synthesizing speech with Hugging Face model: {e}")
    raise
    raise


    def _synthesize_speech_onnx(
    def _synthesize_speech_onnx(
    self,
    self,
    text: str,
    text: str,
    output_path: str,
    output_path: str,
    voice_id: Optional[str] = None,
    voice_id: Optional[str] = None,
    language: Optional[str] = None,
    language: Optional[str] = None,
    **kwargs,
    **kwargs,
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Synthesize speech using an ONNX model.
    Synthesize speech using an ONNX model.


    Args:
    Args:
    text: Text to synthesize
    text: Text to synthesize
    output_path: Path to save the audio file
    output_path: Path to save the audio file
    voice_id: Optional voice ID or speaker ID
    voice_id: Optional voice ID or speaker ID
    language: Optional language code
    language: Optional language code
    **kwargs: Additional parameters for synthesis
    **kwargs: Additional parameters for synthesis


    Returns:
    Returns:
    Dictionary with synthesis results
    Dictionary with synthesis results
    """
    """
    try:
    try:
    # This is a simplified implementation and may need to be adapted for specific models
    # This is a simplified implementation and may need to be adapted for specific models


    # Check if we have a processor
    # Check if we have a processor
    if self.processor:
    if self.processor:
    # Use the processor to prepare inputs
    # Use the processor to prepare inputs
    inputs = self.processor(text=text, return_tensors="np")
    inputs = self.processor(text=text, return_tensors="np")


    # Add speaker embedding if voice_id is provided
    # Add speaker embedding if voice_id is provided
    if voice_id and hasattr(self.processor, "speakers"):
    if voice_id and hasattr(self.processor, "speakers"):
    if voice_id in self.processor.speakers:
    if voice_id in self.processor.speakers:
    speaker_embeddings = self.processor.speakers[voice_id]
    speaker_embeddings = self.processor.speakers[voice_id]
    speaker_embeddings = np.array(speaker_embeddings).reshape(1, -1)
    speaker_embeddings = np.array(speaker_embeddings).reshape(1, -1)
    inputs["speaker_embeddings"] = speaker_embeddings
    inputs["speaker_embeddings"] = speaker_embeddings
    else:
    else:
    logger.warning(
    logger.warning(
    f"Voice ID {voice_id} not found in available voices"
    f"Voice ID {voice_id} not found in available voices"
    )
    )


    # Add language information if provided
    # Add language information if provided
    if language and hasattr(self.processor, "languages"):
    if language and hasattr(self.processor, "languages"):
    if language in self.processor.languages:
    if language in self.processor.languages:
    inputs["language"] = language
    inputs["language"] = language
    else:
    else:
    logger.warning(
    logger.warning(
    f"Language {language} not supported by the model"
    f"Language {language} not supported by the model"
    )
    )
    else:
    else:
    # Basic preprocessing without a processor
    # Basic preprocessing without a processor
    # Convert text to token IDs (this is a placeholder and needs to be adapted)
    # Convert text to token IDs (this is a placeholder and needs to be adapted)
    inputs = {"text": np.array([ord(c) for c in text]).reshape(1, -1)}
    inputs = {"text": np.array([ord(c) for c in text]).reshape(1, -1)}


    # Prepare ONNX inputs
    # Prepare ONNX inputs
    onnx_inputs = {}
    onnx_inputs = {}


    # Map inputs based on model's expected input names
    # Map inputs based on model's expected input names
    for key, value in inputs.items():
    for key, value in inputs.items():
    if key in self.input_names:
    if key in self.input_names:
    onnx_inputs[key] = value
    onnx_inputs[key] = value


    # If no inputs were mapped, use the first input name
    # If no inputs were mapped, use the first input name
    if not onnx_inputs and self.input_names:
    if not onnx_inputs and self.input_names:
    onnx_inputs[self.input_names[0]] = list(inputs.values())[0]
    onnx_inputs[self.input_names[0]] = list(inputs.values())[0]


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


    # Try to get the waveform from outputs
    # Try to get the waveform from outputs
    waveform = outputs[0].squeeze()
    waveform = outputs[0].squeeze()


    # Get sample rate (default to 16000 Hz)
    # Get sample rate (default to 16000 Hz)
    sample_rate = getattr(self.processor, "sampling_rate", 16000)
    sample_rate = getattr(self.processor, "sampling_rate", 16000)


    # Save audio file
    # Save audio file
    if SOUNDFILE_AVAILABLE:
    if SOUNDFILE_AVAILABLE:
    sf.write(output_path, waveform, sample_rate)
    sf.write(output_path, waveform, sample_rate)
    else:
    else:
    # Try to use scipy as fallback
    # Try to use scipy as fallback
    try:
    try:
    (output_path, sample_rate, waveform)
    (output_path, sample_rate, waveform)
except ImportError:
except ImportError:
    raise ImportError(
    raise ImportError(
    "Neither SoundFile nor scipy.io.wavfile is available. Please install one of them."
    "Neither SoundFile nor scipy.io.wavfile is available. Please install one of them."
    )
    )


    # Create result
    # Create result
    result = {
    result = {
    "text": text,
    "text": text,
    "output_path": output_path,
    "output_path": output_path,
    "sample_rate": sample_rate,
    "sample_rate": sample_rate,
    "duration": len(waveform) / sample_rate,
    "duration": len(waveform) / sample_rate,
    "voice_id": voice_id,
    "voice_id": voice_id,
    "language": language,
    "language": language,
    }
    }


    return result
    return result


except Exception as e:
except Exception as e:
    logger.error(f"Error synthesizing speech with ONNX model: {e}")
    logger.error(f"Error synthesizing speech with ONNX model: {e}")
    raise
    raise


    def _synthesize_speech_pytorch(
    def _synthesize_speech_pytorch(
    self,
    self,
    text: str,
    text: str,
    output_path: str,
    output_path: str,
    voice_id: Optional[str] = None,
    voice_id: Optional[str] = None,
    language: Optional[str] = None,
    language: Optional[str] = None,
    **kwargs,
    **kwargs,
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Synthesize speech using a PyTorch model.
    Synthesize speech using a PyTorch model.


    Args:
    Args:
    text: Text to synthesize
    text: Text to synthesize
    output_path: Path to save the audio file
    output_path: Path to save the audio file
    voice_id: Optional voice ID or speaker ID
    voice_id: Optional voice ID or speaker ID
    language: Optional language code
    language: Optional language code
    **kwargs: Additional parameters for synthesis
    **kwargs: Additional parameters for synthesis


    Returns:
    Returns:
    Dictionary with synthesis results
    Dictionary with synthesis results
    """
    """
    try:
    try:
    # Check if we have a processor
    # Check if we have a processor
    if self.processor:
    if self.processor:
    # Use the processor to prepare inputs
    # Use the processor to prepare inputs
    inputs = self.processor(text=text, return_tensors="pt").to(self.device)
    inputs = self.processor(text=text, return_tensors="pt").to(self.device)


    # Add speaker embedding if voice_id is provided
    # Add speaker embedding if voice_id is provided
    if voice_id and hasattr(self.processor, "speakers"):
    if voice_id and hasattr(self.processor, "speakers"):
    if voice_id in self.processor.speakers:
    if voice_id in self.processor.speakers:
    speaker_embeddings = self.processor.speakers[voice_id]
    speaker_embeddings = self.processor.speakers[voice_id]
    speaker_embeddings = (
    speaker_embeddings = (
    torch.tensor(speaker_embeddings)
    torch.tensor(speaker_embeddings)
    .unsqueeze(0)
    .unsqueeze(0)
    .to(self.device)
    .to(self.device)
    )
    )
    inputs["speaker_embeddings"] = speaker_embeddings
    inputs["speaker_embeddings"] = speaker_embeddings
    else:
    else:
    logger.warning(
    logger.warning(
    f"Voice ID {voice_id} not found in available voices"
    f"Voice ID {voice_id} not found in available voices"
    )
    )


    # Add language information if provided
    # Add language information if provided
    if language and hasattr(self.processor, "languages"):
    if language and hasattr(self.processor, "languages"):
    if language in self.processor.languages:
    if language in self.processor.languages:
    inputs["language"] = language
    inputs["language"] = language
    else:
    else:
    logger.warning(
    logger.warning(
    f"Language {language} not supported by the model"
    f"Language {language} not supported by the model"
    )
    )


    # Generate speech
    # Generate speech
    with torch.no_grad():
    with torch.no_grad():
    outputs = self.model(**inputs)
    outputs = self.model(**inputs)


    # Get waveform
    # Get waveform
    if hasattr(outputs, "waveform"):
    if hasattr(outputs, "waveform"):
    waveform = outputs.waveform.cpu().numpy()[0]
    waveform = outputs.waveform.cpu().numpy()[0]
    elif hasattr(outputs, "audio"):
    elif hasattr(outputs, "audio"):
    waveform = outputs.audio.cpu().numpy()[0]
    waveform = outputs.audio.cpu().numpy()[0]
    else:
    else:
    # Try to get the first output
    # Try to get the first output
    waveform = list(outputs.values())[0].cpu().numpy()[0]
    waveform = list(outputs.values())[0].cpu().numpy()[0]
    else:
    else:
    # Basic inference without a processor
    # Basic inference without a processor
    # Convert text to tensor (this is a placeholder and needs to be adapted)
    # Convert text to tensor (this is a placeholder and needs to be adapted)
    text_tensor = torch.tensor([[ord(c) for c in text]]).to(self.device)
    text_tensor = torch.tensor([[ord(c) for c in text]]).to(self.device)


    # Run inference
    # Run inference
    with torch.no_grad():
    with torch.no_grad():
    outputs = self.model(text_tensor)
    outputs = self.model(text_tensor)


    # Get waveform
    # Get waveform
    if isinstance(outputs, torch.Tensor):
    if isinstance(outputs, torch.Tensor):
    waveform = outputs.cpu().numpy()[0]
    waveform = outputs.cpu().numpy()[0]
    else:
    else:
    # Try to get the first output
    # Try to get the first output
    waveform = list(outputs.values())[0].cpu().numpy()[0]
    waveform = list(outputs.values())[0].cpu().numpy()[0]


    # Get sample rate (default to 16000 Hz)
    # Get sample rate (default to 16000 Hz)
    sample_rate = getattr(self.processor, "sampling_rate", 16000)
    sample_rate = getattr(self.processor, "sampling_rate", 16000)


    # Save audio file
    # Save audio file
    if SOUNDFILE_AVAILABLE:
    if SOUNDFILE_AVAILABLE:
    sf.write(output_path, waveform, sample_rate)
    sf.write(output_path, waveform, sample_rate)
    else:
    else:
    # Try to use scipy as fallback
    # Try to use scipy as fallback
    try:
    try:
    (output_path, sample_rate, waveform)
    (output_path, sample_rate, waveform)
except ImportError:
except ImportError:
    raise ImportError(
    raise ImportError(
    "Neither SoundFile nor scipy.io.wavfile is available. Please install one of them."
    "Neither SoundFile nor scipy.io.wavfile is available. Please install one of them."
    )
    )


    # Create result
    # Create result
    result = {
    result = {
    "text": text,
    "text": text,
    "output_path": output_path,
    "output_path": output_path,
    "sample_rate": sample_rate,
    "sample_rate": sample_rate,
    "duration": len(waveform) / sample_rate,
    "duration": len(waveform) / sample_rate,
    "voice_id": voice_id,
    "voice_id": voice_id,
    "language": language,
    "language": language,
    }
    }


    return result
    return result


except Exception as e:
except Exception as e:
    logger.error(f"Error synthesizing speech with PyTorch model: {e}")
    logger.error(f"Error synthesizing speech with PyTorch model: {e}")
    raise
    raise


    def get_available_voices(self) -> List[Dict[str, Any]]:
    def get_available_voices(self) -> List[Dict[str, Any]]:
    """
    """
    Get a list of available voices for text-to-speech.
    Get a list of available voices for text-to-speech.


    Returns:
    Returns:
    List of voice information dictionaries
    List of voice information dictionaries
    """
    """
    if not self.model:
    if not self.model:
    self.load()
    self.load()


    if self.model_type != "text-to-speech":
    if self.model_type != "text-to-speech":
    raise ValueError(
    raise ValueError(
    f"Model type {self.model_type} does not support text-to-speech"
    f"Model type {self.model_type} does not support text-to-speech"
    )
    )


    voices = []
    voices = []


    try:
    try:
    # Check if the processor has speaker information
    # Check if the processor has speaker information
    if hasattr(self.processor, "speakers"):
    if hasattr(self.processor, "speakers"):
    for speaker_id, _ in self.processor.speakers.items():
    for speaker_id, _ in self.processor.speakers.items():
    voice_info = {"id": speaker_id, "name": speaker_id}
    voice_info = {"id": speaker_id, "name": speaker_id}
    voices.append(voice_info)
    voices.append(voice_info)


    # Check if the model config has speaker information
    # Check if the model config has speaker information
    elif hasattr(self.model, "config") and hasattr(
    elif hasattr(self.model, "config") and hasattr(
    self.model.config, "speaker_ids"
    self.model.config, "speaker_ids"
    ):
    ):
    for speaker_id, speaker_name in self.model.config.speaker_ids.items():
    for speaker_id, speaker_name in self.model.config.speaker_ids.items():
    voice_info = {"id": speaker_id, "name": speaker_name}
    voice_info = {"id": speaker_id, "name": speaker_name}
    voices.append(voice_info)
    voices.append(voice_info)


    return voices
    return voices


except Exception as e:
except Exception as e:
    logger.error(f"Error getting available voices: {e}")
    logger.error(f"Error getting available voices: {e}")
    return []
    return []


    def classify_audio(self, audio_path: str, **kwargs) -> Dict[str, float]:
    def classify_audio(self, audio_path: str, **kwargs) -> Dict[str, float]:
    """
    """
    Classify audio using the model.
    Classify audio using the model.


    Args:
    Args:
    audio_path: Path to the audio file
    audio_path: Path to the audio file
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


    if self.model_type != "audio-classification":
    if self.model_type != "audio-classification":
    raise ValueError(
    raise ValueError(
    f"Model type {self.model_type} does not support audio classification"
    f"Model type {self.model_type} does not support audio classification"
    )
    )


    try:
    try:
    # Load audio
    # Load audio
    audio_array, sample_rate = self._load_audio(audio_path)
    audio_array, sample_rate = self._load_audio(audio_path)


    if self.model_format == "huggingface":
    if self.model_format == "huggingface":
    return self._classify_audio_huggingface(
    return self._classify_audio_huggingface(
    audio_array, sample_rate, **kwargs
    audio_array, sample_rate, **kwargs
    )
    )
    elif self.model_format == "onnx":
    elif self.model_format == "onnx":
    return self._classify_audio_onnx(audio_array, sample_rate, **kwargs)
    return self._classify_audio_onnx(audio_array, sample_rate, **kwargs)
    elif self.model_format == "pytorch":
    elif self.model_format == "pytorch":
    return self._classify_audio_pytorch(audio_array, sample_rate, **kwargs)
    return self._classify_audio_pytorch(audio_array, sample_rate, **kwargs)
    else:
    else:
    raise ValueError(f"Unsupported model format: {self.model_format}")
    raise ValueError(f"Unsupported model format: {self.model_format}")


except Exception as e:
except Exception as e:
    logger.error(f"Error classifying audio: {e}")
    logger.error(f"Error classifying audio: {e}")
    raise
    raise


    def _classify_audio_huggingface(
    def _classify_audio_huggingface(
    self, audio_array: np.ndarray, sample_rate: int, **kwargs
    self, audio_array: np.ndarray, sample_rate: int, **kwargs
    ) -> Dict[str, float]:
    ) -> Dict[str, float]:
    """
    """
    Classify audio using a Hugging Face model.
    Classify audio using a Hugging Face model.


    Args:
    Args:
    audio_array: Audio data as numpy array
    audio_array: Audio data as numpy array
    sample_rate: Sample rate of the audio
    sample_rate: Sample rate of the audio
    **kwargs: Additional parameters for classification
    **kwargs: Additional parameters for classification


    Returns:
    Returns:
    Dictionary of class labels and scores
    Dictionary of class labels and scores
    """
    """
    try:
    try:
    # Check if we need to resample
    # Check if we need to resample
    model_sample_rate = getattr(self.processor, "sampling_rate", 16000)
    model_sample_rate = getattr(self.processor, "sampling_rate", 16000)
    if sample_rate != model_sample_rate:
    if sample_rate != model_sample_rate:
    if LIBROSA_AVAILABLE:
    if LIBROSA_AVAILABLE:
    logger.info(
    logger.info(
    f"Resampling audio from {sample_rate} Hz to {model_sample_rate} Hz"
    f"Resampling audio from {sample_rate} Hz to {model_sample_rate} Hz"
    )
    )
    audio_array = librosa.resample(
    audio_array = librosa.resample(
    audio_array, orig_sr=sample_rate, target_sr=model_sample_rate
    audio_array, orig_sr=sample_rate, target_sr=model_sample_rate
    )
    )
    sample_rate = model_sample_rate
    sample_rate = model_sample_rate
    else:
    else:
    logger.warning(
    logger.warning(
    f"Audio sample rate ({sample_rate} Hz) doesn't match model sample rate ({model_sample_rate} Hz), but librosa is not available for resampling"
    f"Audio sample rate ({sample_rate} Hz) doesn't match model sample rate ({model_sample_rate} Hz), but librosa is not available for resampling"
    )
    )


    # Process audio
    # Process audio
    inputs = self.processor(
    inputs = self.processor(
    audio_array, sampling_rate=sample_rate, return_tensors="pt"
    audio_array, sampling_rate=sample_rate, return_tensors="pt"
    ).to(self.device)
    ).to(self.device)


    # Run inference
    # Run inference
    with torch.no_grad():
    with torch.no_grad():
    outputs = self.model(**inputs)
    outputs = self.model(**inputs)


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


except Exception as e:
except Exception as e:
    logger.error(f"Error classifying audio with Hugging Face model: {e}")
    logger.error(f"Error classifying audio with Hugging Face model: {e}")
    raise
    raise


    def _classify_audio_onnx(
    def _classify_audio_onnx(
    self, audio_array: np.ndarray, sample_rate: int, **kwargs
    self, audio_array: np.ndarray, sample_rate: int, **kwargs
    ) -> Dict[str, float]:
    ) -> Dict[str, float]:
    """
    """
    Classify audio using an ONNX model.
    Classify audio using an ONNX model.


    Args:
    Args:
    audio_array: Audio data as numpy array
    audio_array: Audio data as numpy array
    sample_rate: Sample rate of the audio
    sample_rate: Sample rate of the audio
    **kwargs: Additional parameters for classification
    **kwargs: Additional parameters for classification


    Returns:
    Returns:
    Dictionary of class labels and scores
    Dictionary of class labels and scores
    """
    """
    try:
    try:
    # This is a simplified implementation and may need to be adapted for specific models
    # This is a simplified implementation and may need to be adapted for specific models


    # Check if we have a processor
    # Check if we have a processor
    if self.processor:
    if self.processor:
    # Use the processor to prepare inputs
    # Use the processor to prepare inputs
    inputs = self.processor(
    inputs = self.processor(
    audio_array, sampling_rate=sample_rate, return_tensors="np"
    audio_array, sampling_rate=sample_rate, return_tensors="np"
    )
    )


    # Extract the input features
    # Extract the input features
    if "input_features" in inputs:
    if "input_features" in inputs:
    input_data = inputs.input_features
    input_data = inputs.input_features
    elif "input_values" in inputs:
    elif "input_values" in inputs:
    input_data = inputs.input_values
    input_data = inputs.input_values
    else:
    else:
    # Use the first input as fallback
    # Use the first input as fallback
    input_data = list(inputs.values())[0]
    input_data = list(inputs.values())[0]
    else:
    else:
    # Basic preprocessing without a processor
    # Basic preprocessing without a processor
    # Resample if needed (assuming 16kHz is common for audio models)
    # Resample if needed (assuming 16kHz is common for audio models)
    if sample_rate != 16000:
    if sample_rate != 16000:
    if LIBROSA_AVAILABLE:
    if LIBROSA_AVAILABLE:
    logger.info(
    logger.info(
    f"Resampling audio from {sample_rate} Hz to 16000 Hz"
    f"Resampling audio from {sample_rate} Hz to 16000 Hz"
    )
    )
    audio_array = librosa.resample(
    audio_array = librosa.resample(
    audio_array, orig_sr=sample_rate, target_sr=16000
    audio_array, orig_sr=sample_rate, target_sr=16000
    )
    )
    else:
    else:
    logger.warning(
    logger.warning(
    "Audio sample rate doesn't match 16000 Hz, but librosa is not available for resampling"
    "Audio sample rate doesn't match 16000 Hz, but librosa is not available for resampling"
    )
    )


    # Convert to float32 and normalize
    # Convert to float32 and normalize
    input_data = audio_array.astype(np.float32)
    input_data = audio_array.astype(np.float32)


    # Add batch dimension if needed
    # Add batch dimension if needed
    if input_data.ndim == 1:
    if input_data.ndim == 1:
    input_data = np.expand_dims(input_data, axis=0)
    input_data = np.expand_dims(input_data, axis=0)


    # Prepare ONNX inputs
    # Prepare ONNX inputs
    onnx_inputs = {}
    onnx_inputs = {}


    # Map inputs based on model's expected input names
    # Map inputs based on model's expected input names
    if len(self.input_names) == 1:
    if len(self.input_names) == 1:
    # If there's only one input, use it directly
    # If there's only one input, use it directly
    onnx_inputs[self.input_names[0]] = input_data
    onnx_inputs[self.input_names[0]] = input_data
    else:
    else:
    # Try to map to common input names
    # Try to map to common input names
    if "input_features" in self.input_names:
    if "input_features" in self.input_names:
    onnx_inputs["input_features"] = input_data
    onnx_inputs["input_features"] = input_data
    elif "input_values" in self.input_names:
    elif "input_values" in self.input_names:
    onnx_inputs["input_values"] = input_data
    onnx_inputs["input_values"] = input_data
    elif "input" in self.input_names:
    elif "input" in self.input_names:
    onnx_inputs["input"] = input_data
    onnx_inputs["input"] = input_data
    else:
    else:
    # Use the first input name
    # Use the first input name
    onnx_inputs[self.input_names[0]] = input_data
    onnx_inputs[self.input_names[0]] = input_data


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
    labels = []
    labels = []


    # Try to get labels from metadata
    # Try to get labels from metadata
    if hasattr(self, "labels") and self.labels:
    if hasattr(self, "labels") and self.labels:
    labels = self.labels
    labels = self.labels
    else:
    else:
    # Try to load labels from model metadata
    # Try to load labels from model metadata
    if hasattr(self.model, "get_modelmeta"):
    if hasattr(self.model, "get_modelmeta"):
    metadata = self.model.get_modelmeta()
    metadata = self.model.get_modelmeta()
    if metadata and metadata.custom_metadata_map:
    if metadata and metadata.custom_metadata_map:
    if "id2label" in metadata.custom_metadata_map:
    if "id2label" in metadata.custom_metadata_map:
    try:
    try:
    id2label = json.loads(
    id2label = json.loads(
    metadata.custom_metadata_map["id2label"]
    metadata.custom_metadata_map["id2label"]
    )
    )
    labels = [
    labels = [
    id2label.get(str(i), f"Class {i}")
    id2label.get(str(i), f"Class {i}")
    for i in range(len(probs))
    for i in range(len(probs))
    ]
    ]
except Exception:
except Exception:
    pass
    pass


    # Fallback to generic labels
    # Fallback to generic labels
    if not labels:
    if not labels:
    labels = [f"Class {i}" for i in range(len(probs))]
    labels = [f"Class {i}" for i in range(len(probs))]


    # Create result dictionary
    # Create result dictionary
    result = {label: float(prob) for label, prob in zip(labels, probs)}
    result = {label: float(prob) for label, prob in zip(labels, probs)}


    return result
    return result


except Exception as e:
except Exception as e:
    logger.error(f"Error classifying audio with ONNX model: {e}")
    logger.error(f"Error classifying audio with ONNX model: {e}")
    raise
    raise


    def _classify_audio_pytorch(
    def _classify_audio_pytorch(
    self, audio_array: np.ndarray, sample_rate: int, **kwargs
    self, audio_array: np.ndarray, sample_rate: int, **kwargs
    ) -> Dict[str, float]:
    ) -> Dict[str, float]:
    """
    """
    Classify audio using a PyTorch model.
    Classify audio using a PyTorch model.


    Args:
    Args:
    audio_array: Audio data as numpy array
    audio_array: Audio data as numpy array
    sample_rate: Sample rate of the audio
    sample_rate: Sample rate of the audio
    **kwargs: Additional parameters for classification
    **kwargs: Additional parameters for classification


    Returns:
    Returns:
    Dictionary of class labels and scores
    Dictionary of class labels and scores
    """
    """
    try:
    try:
    # Check if we have a processor
    # Check if we have a processor
    if self.processor:
    if self.processor:
    # Use the processor to prepare inputs
    # Use the processor to prepare inputs
    inputs = self.processor(
    inputs = self.processor(
    audio_array, sampling_rate=sample_rate, return_tensors="pt"
    audio_array, sampling_rate=sample_rate, return_tensors="pt"
    ).to(self.device)
    ).to(self.device)


    # Run inference
    # Run inference
    with torch.no_grad():
    with torch.no_grad():
    outputs = self.model(**inputs)
    outputs = self.model(**inputs)


    # Get logits
    # Get logits
    if hasattr(outputs, "logits"):
    if hasattr(outputs, "logits"):
    logits = outputs.logits
    logits = outputs.logits
    else:
    else:
    # Try to get the first output
    # Try to get the first output
    logits = list(outputs.values())[0]
    logits = list(outputs.values())[0]
    else:
    else:
    # Basic inference without a processor
    # Basic inference without a processor
    # Convert to tensor
    # Convert to tensor
    audio_tensor = (
    audio_tensor = (
    torch.tensor(audio_array, dtype=torch.float32)
    torch.tensor(audio_array, dtype=torch.float32)
    .unsqueeze(0)
    .unsqueeze(0)
    .to(self.device)
    .to(self.device)
    )
    )


    # Run inference
    # Run inference
    with torch.no_grad():
    with torch.no_grad():
    outputs = self.model(audio_tensor)
    outputs = self.model(audio_tensor)


    # Get logits
    # Get logits
    if isinstance(outputs, torch.Tensor):
    if isinstance(outputs, torch.Tensor):
    logits = outputs
    logits = outputs
    elif hasattr(outputs, "logits"):
    elif hasattr(outputs, "logits"):
    logits = outputs.logits
    logits = outputs.logits
    else:
    else:
    # Try to get the first output
    # Try to get the first output
    logits = list(outputs.values())[0]
    logits = list(outputs.values())[0]


    # Convert logits to probabilities
    # Convert logits to probabilities
    probs = torch.nn.functional.softmax(logits, dim=-1)[0].cpu().numpy()
    probs = torch.nn.functional.softmax(logits, dim=-1)[0].cpu().numpy()


    # Get class labels
    # Get class labels
    labels = []
    labels = []


    # Try to get labels from model config
    # Try to get labels from model config
    if hasattr(self.model, "config") and hasattr(self.model.config, "id2label"):
    if hasattr(self.model, "config") and hasattr(self.model.config, "id2label"):
    labels = list(self.model.config.id2label.values())
    labels = list(self.model.config.id2label.values())
    elif hasattr(self, "labels") and self.labels:
    elif hasattr(self, "labels") and self.labels:
    labels = self.labels
    labels = self.labels
    else:
    else:
    # Fallback to generic labels
    # Fallback to generic labels
    labels = [f"Class {i}" for i in range(len(probs))]
    labels = [f"Class {i}" for i in range(len(probs))]


    # Create result dictionary
    # Create result dictionary
    result = {label: float(prob) for label, prob in zip(labels, probs)}
    result = {label: float(prob) for label, prob in zip(labels, probs)}


    return result
    return result


except Exception as e:
except Exception as e:
    logger.error(f"Error classifying audio with PyTorch model: {e}")
    logger.error(f"Error classifying audio with PyTorch model: {e}")
    raise
    raise


    def detect_sound_events(
    def detect_sound_events(
    self, audio_path: str, threshold: float = 0.5, **kwargs
    self, audio_path: str, threshold: float = 0.5, **kwargs
    ) -> List[Dict[str, Any]]:
    ) -> List[Dict[str, Any]]:
    """
    """
    Detect sound events in an audio file.
    Detect sound events in an audio file.


    Args:
    Args:
    audio_path: Path to the audio file
    audio_path: Path to the audio file
    threshold: Confidence threshold for detections
    threshold: Confidence threshold for detections
    **kwargs: Additional parameters for detection
    **kwargs: Additional parameters for detection


    Returns:
    Returns:
    List of detected sound events with timestamps and scores
    List of detected sound events with timestamps and scores
    """
    """
    if not self.model:
    if not self.model:
    self.load()
    self.load()


    if (
    if (
    self.model_type != "audio-classification"
    self.model_type != "audio-classification"
    and self.model_type != "sound-event-detection"
    and self.model_type != "sound-event-detection"
    ):
    ):
    raise ValueError(
    raise ValueError(
    f"Model type {self.model_type} does not support sound event detection"
    f"Model type {self.model_type} does not support sound event detection"
    )
    )


    try:
    try:
    # Load audio
    # Load audio
    audio_array, sample_rate = self._load_audio(audio_path)
    audio_array, sample_rate = self._load_audio(audio_path)


    # For basic sound event detection, we'll use a sliding window approach
    # For basic sound event detection, we'll use a sliding window approach
    # This is a simplified implementation and may need to be adapted for specific models
    # This is a simplified implementation and may need to be adapted for specific models


    # Define window size and hop length (in seconds)
    # Define window size and hop length (in seconds)
    window_size = kwargs.get("window_size", 1.0)  # 1 second window
    window_size = kwargs.get("window_size", 1.0)  # 1 second window
    hop_length = kwargs.get("hop_length", 0.5)  # 0.5 second hop
    hop_length = kwargs.get("hop_length", 0.5)  # 0.5 second hop


    # Convert to samples
    # Convert to samples
    window_samples = int(window_size * sample_rate)
    window_samples = int(window_size * sample_rate)
    hop_samples = int(hop_length * sample_rate)
    hop_samples = int(hop_length * sample_rate)


    # Initialize results
    # Initialize results
    events = []
    events = []


    # Process audio in windows
    # Process audio in windows
    for i in range(0, len(audio_array) - window_samples + 1, hop_samples):
    for i in range(0, len(audio_array) - window_samples + 1, hop_samples):
    # Extract window
    # Extract window
    window = audio_array[i : i + window_samples]
    window = audio_array[i : i + window_samples]


    # Classify window
    # Classify window
    if self.model_format == "huggingface":
    if self.model_format == "huggingface":
    results = self._classify_audio_huggingface(
    results = self._classify_audio_huggingface(
    window, sample_rate, **kwargs
    window, sample_rate, **kwargs
    )
    )
    elif self.model_format == "onnx":
    elif self.model_format == "onnx":
    results = self._classify_audio_onnx(window, sample_rate, **kwargs)
    results = self._classify_audio_onnx(window, sample_rate, **kwargs)
    elif self.model_format == "pytorch":
    elif self.model_format == "pytorch":
    results = self._classify_audio_pytorch(
    results = self._classify_audio_pytorch(
    window, sample_rate, **kwargs
    window, sample_rate, **kwargs
    )
    )
    else:
    else:
    raise ValueError(f"Unsupported model format: {self.model_format}")
    raise ValueError(f"Unsupported model format: {self.model_format}")


    # Filter by threshold
    # Filter by threshold
    for label, score in results.items():
    for label, score in results.items():
    if score >= threshold:
    if score >= threshold:
    # Calculate timestamp
    # Calculate timestamp
    start_time = i / sample_rate
    start_time = i / sample_rate
    end_time = (i + window_samples) / sample_rate
    end_time = (i + window_samples) / sample_rate


    event = {
    event = {
    "label": label,
    "label": label,
    "score": float(score),
    "score": float(score),
    "start_time": float(start_time),
    "start_time": float(start_time),
    "end_time": float(end_time),
    "end_time": float(end_time),
    }
    }


    events.append(event)
    events.append(event)


    return events
    return events


except Exception as e:
except Exception as e:
    logger.error(f"Error detecting sound events: {e}")
    logger.error(f"Error detecting sound events: {e}")
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
    # Create audio model
    # Create audio model
    model = AudioModel(model_path=model_path, model_type="speech-recognition")
    model = AudioModel(model_path=model_path, model_type="speech-recognition")


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
    else:
    else:
    print(f"Model file not found: {model_path}")
    print(f"Model file not found: {model_path}")
    print("Please specify a valid model path.")
    print("Please specify a valid model path.")