"""
"""
Benchmark runner for AI models.
Benchmark runner for AI models.


This module provides functionality for running benchmarks on AI models.
This module provides functionality for running benchmarks on AI models.
"""
"""


import gc
import gc
import json
import json
import logging
import logging
import os
import os
import time
import time
from typing import Any, Dict, List, Tuple
from typing import Any, Dict, List, Tuple


from .benchmark_config import BenchmarkConfig, BenchmarkType
from .benchmark_config import BenchmarkConfig, BenchmarkType
from .benchmark_result import BenchmarkResult
from .benchmark_result import BenchmarkResult


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
    import torch
    import torch


    TORCH_AVAILABLE = True
    TORCH_AVAILABLE = True
except ImportError:
except ImportError:
    logger.warning("PyTorch not available. Some benchmarks may not work.")
    logger.warning("PyTorch not available. Some benchmarks may not work.")
    TORCH_AVAILABLE = False
    TORCH_AVAILABLE = False


    try:
    try:
    import transformers
    import transformers


    TRANSFORMERS_AVAILABLE = True
    TRANSFORMERS_AVAILABLE = True
except ImportError:
except ImportError:
    logger.warning("Transformers not available. Some benchmarks may not work.")
    logger.warning("Transformers not available. Some benchmarks may not work.")
    TRANSFORMERS_AVAILABLE = False
    TRANSFORMERS_AVAILABLE = False


    try:
    try:
    import psutil
    import psutil


    PSUTIL_AVAILABLE = True
    PSUTIL_AVAILABLE = True
except ImportError:
except ImportError:
    logger.warning("psutil not available. Memory benchmarks will be limited.")
    logger.warning("psutil not available. Memory benchmarks will be limited.")
    PSUTIL_AVAILABLE = False
    PSUTIL_AVAILABLE = False


    try:
    try:
    import numpy as np
    import numpy as np


    NUMPY_AVAILABLE = True
    NUMPY_AVAILABLE = True
except ImportError:
except ImportError:
    logger.warning("NumPy not available. Some benchmarks may not work.")
    logger.warning("NumPy not available. Some benchmarks may not work.")
    NUMPY_AVAILABLE = False
    NUMPY_AVAILABLE = False


    try:
    try:
    from rouge_score import rouge_scorer
    from rouge_score import rouge_scorer


    ROUGE_AVAILABLE = True
    ROUGE_AVAILABLE = True
except ImportError:
except ImportError:
    logger.warning("rouge_score not available. ROUGE benchmarks will not work.")
    logger.warning("rouge_score not available. ROUGE benchmarks will not work.")
    ROUGE_AVAILABLE = False
    ROUGE_AVAILABLE = False




    class BenchmarkRunner:
    class BenchmarkRunner:
    """
    """
    Runner for benchmarking AI models.
    Runner for benchmarking AI models.
    """
    """


    def __init__(self, config: BenchmarkConfig):
    def __init__(self, config: BenchmarkConfig):
    """
    """
    Initialize the benchmark runner.
    Initialize the benchmark runner.


    Args:
    Args:
    config: Benchmark configuration
    config: Benchmark configuration
    """
    """
    self.config = config
    self.config = config
    self.model = None
    self.model = None
    self.tokenizer = None
    self.tokenizer = None
    self.input_data = self._load_input_data()
    self.input_data = self._load_input_data()


    def _load_input_data(self) -> List[str]:
    def _load_input_data(self) -> List[str]:
    """
    """
    Load input data for benchmarking.
    Load input data for benchmarking.


    Returns:
    Returns:
    List of input strings
    List of input strings
    """
    """
    if self.config.input_data:
    if self.config.input_data:
    if isinstance(self.config.input_data, list):
    if isinstance(self.config.input_data, list):
    return self.config.input_data
    return self.config.input_data
    else:
    else:
    return [self.config.input_data]
    return [self.config.input_data]
    elif self.config.input_file:
    elif self.config.input_file:
    if not os.path.exists(self.config.input_file):
    if not os.path.exists(self.config.input_file):
    raise FileNotFoundError(
    raise FileNotFoundError(
    f"Input file not found: {self.config.input_file}"
    f"Input file not found: {self.config.input_file}"
    )
    )


    with open(self.config.input_file, "r") as f:
    with open(self.config.input_file, "r") as f:
    if self.config.input_file.endswith(".json"):
    if self.config.input_file.endswith(".json"):
    data = json.load(f)
    data = json.load(f)
    if isinstance(data, list):
    if isinstance(data, list):
    return data
    return data
    else:
    else:
    return [json.dumps(data)]
    return [json.dumps(data)]
    else:
    else:
    return f.read().splitlines()
    return f.read().splitlines()
    else:
    else:
    # Default input data
    # Default input data
    return [
    return [
    "Hello, world!",
    "Hello, world!",
    "How are you today?",
    "How are you today?",
    "What is the meaning of life?",
    "What is the meaning of life?",
    ]
    ]


    def _load_model(self) -> Tuple[Any, Any]:
    def _load_model(self) -> Tuple[Any, Any]:
    """
    """
    Load the model for benchmarking.
    Load the model for benchmarking.


    Returns:
    Returns:
    Tuple of (model, tokenizer)
    Tuple of (model, tokenizer)
    """
    """
    if self.config.model_type == "text-generation":
    if self.config.model_type == "text-generation":
    if not TRANSFORMERS_AVAILABLE:
    if not TRANSFORMERS_AVAILABLE:
    raise ImportError(
    raise ImportError(
    "Transformers library is required for text generation models"
    "Transformers library is required for text generation models"
    )
    )


    logger.info(f"Loading model: {self.config.model_path}")
    logger.info(f"Loading model: {self.config.model_path}")
    tokenizer = transformers.AutoTokenizer.from_pretrained(
    tokenizer = transformers.AutoTokenizer.from_pretrained(
    self.config.model_path
    self.config.model_path
    )
    )
    model = transformers.AutoModelForCausalLM.from_pretrained(
    model = transformers.AutoModelForCausalLM.from_pretrained(
    self.config.model_path,
    self.config.model_path,
    device_map=self.config.device if self.config.device != "cpu" else None,
    device_map=self.config.device if self.config.device != "cpu" else None,
    torch_dtype=torch.float16 if self.config.device == "cuda" else None,
    torch_dtype=torch.float16 if self.config.device == "cuda" else None,
    )
    )
    return model, tokenizer
    return model, tokenizer


    elif self.config.model_type == "embedding":
    elif self.config.model_type == "embedding":
    if not TRANSFORMERS_AVAILABLE:
    if not TRANSFORMERS_AVAILABLE:
    raise ImportError(
    raise ImportError(
    "Transformers library is required for embedding models"
    "Transformers library is required for embedding models"
    )
    )


    logger.info(f"Loading model: {self.config.model_path}")
    logger.info(f"Loading model: {self.config.model_path}")
    tokenizer = transformers.AutoTokenizer.from_pretrained(
    tokenizer = transformers.AutoTokenizer.from_pretrained(
    self.config.model_path
    self.config.model_path
    )
    )
    model = transformers.AutoModel.from_pretrained(
    model = transformers.AutoModel.from_pretrained(
    self.config.model_path,
    self.config.model_path,
    device_map=self.config.device if self.config.device != "cpu" else None,
    device_map=self.config.device if self.config.device != "cpu" else None,
    torch_dtype=torch.float16 if self.config.device == "cuda" else None,
    torch_dtype=torch.float16 if self.config.device == "cuda" else None,
    )
    )
    return model, tokenizer
    return model, tokenizer


    else:
    else:
    raise ValueError(f"Unsupported model type: {self.config.model_type}")
    raise ValueError(f"Unsupported model type: {self.config.model_type}")


    def _run_inference(self, model: Any, tokenizer: Any, input_text: str) -> Any:
    def _run_inference(self, model: Any, tokenizer: Any, input_text: str) -> Any:
    """
    """
    Run inference with the model.
    Run inference with the model.


    Args:
    Args:
    model: The model to use
    model: The model to use
    tokenizer: The tokenizer to use
    tokenizer: The tokenizer to use
    input_text: Input text for inference
    input_text: Input text for inference


    Returns:
    Returns:
    Model output
    Model output
    """
    """
    if self.config.model_type == "text-generation":
    if self.config.model_type == "text-generation":
    inputs = tokenizer(input_text, return_tensors="pt")
    inputs = tokenizer(input_text, return_tensors="pt")
    if self.config.device == "cuda" and TORCH_AVAILABLE:
    if self.config.device == "cuda" and TORCH_AVAILABLE:
    inputs = {k: v.cuda() for k, v in inputs.items()}
    inputs = {k: v.cuda() for k, v in inputs.items()}


    with torch.no_grad():
    with torch.no_grad():
    outputs = model.generate(
    outputs = model.generate(
    **inputs,
    **inputs,
    max_length=self.config.max_tokens,
    max_length=self.config.max_tokens,
    **self.config.additional_params,
    **self.config.additional_params,
    )
    )


    return tokenizer.decode(outputs[0], skip_special_tokens=True)
    return tokenizer.decode(outputs[0], skip_special_tokens=True)


    elif self.config.model_type == "embedding":
    elif self.config.model_type == "embedding":
    inputs = tokenizer(
    inputs = tokenizer(
    input_text, return_tensors="pt", padding=True, truncation=True
    input_text, return_tensors="pt", padding=True, truncation=True
    )
    )
    if self.config.device == "cuda" and TORCH_AVAILABLE:
    if self.config.device == "cuda" and TORCH_AVAILABLE:
    inputs = {k: v.cuda() for k, v in inputs.items()}
    inputs = {k: v.cuda() for k, v in inputs.items()}


    with torch.no_grad():
    with torch.no_grad():
    outputs = model(**inputs)
    outputs = model(**inputs)


    # Get embeddings from the last hidden state
    # Get embeddings from the last hidden state
    embeddings = outputs.last_hidden_state.mean(dim=1)
    embeddings = outputs.last_hidden_state.mean(dim=1)
    return embeddings.cpu().numpy() if TORCH_AVAILABLE else embeddings.numpy()
    return embeddings.cpu().numpy() if TORCH_AVAILABLE else embeddings.numpy()


    else:
    else:
    raise ValueError(f"Unsupported model type: {self.config.model_type}")
    raise ValueError(f"Unsupported model type: {self.config.model_type}")


    def _measure_latency(self) -> Tuple[List[float], List[Any]]:
    def _measure_latency(self) -> Tuple[List[float], List[Any]]:
    """
    """
    Measure inference latency.
    Measure inference latency.


    Returns:
    Returns:
    Tuple of (run times in ms, outputs)
    Tuple of (run times in ms, outputs)
    """
    """
    logger.info("Measuring inference latency...")
    logger.info("Measuring inference latency...")


    model, tokenizer = self._load_model()
    model, tokenizer = self._load_model()
    run_times = []
    run_times = []
    outputs = []
    outputs = []


    # Warmup runs
    # Warmup runs
    for _ in range(self.config.warmup_runs):
    for _ in range(self.config.warmup_runs):
    self._run_inference(model, tokenizer, self.input_data[0])
    self._run_inference(model, tokenizer, self.input_data[0])


    # Benchmark runs
    # Benchmark runs
    for i in range(min(self.config.num_runs, len(self.input_data))):
    for i in range(min(self.config.num_runs, len(self.input_data))):
    input_text = self.input_data[i % len(self.input_data)]
    input_text = self.input_data[i % len(self.input_data)]


    start_time = time.time()
    start_time = time.time()
    output = self._run_inference(model, tokenizer, input_text)
    output = self._run_inference(model, tokenizer, input_text)
    end_time = time.time()
    end_time = time.time()


    run_time_ms = (end_time - start_time) * 1000
    run_time_ms = (end_time - start_time) * 1000
    run_times.append(run_time_ms)
    run_times.append(run_time_ms)
    outputs.append(output)
    outputs.append(output)


    logger.info(f"Run {i+1}/{self.config.num_runs}: {run_time_ms:.2f} ms")
    logger.info(f"Run {i+1}/{self.config.num_runs}: {run_time_ms:.2f} ms")


    return run_times, outputs
    return run_times, outputs


    def _measure_throughput(self) -> float:
    def _measure_throughput(self) -> float:
    """
    """
    Measure inference throughput.
    Measure inference throughput.


    Returns:
    Returns:
    Throughput in tokens per second
    Throughput in tokens per second
    """
    """
    logger.info("Measuring inference throughput...")
    logger.info("Measuring inference throughput...")


    model, tokenizer = self._load_model()
    model, tokenizer = self._load_model()


    # Prepare batch input
    # Prepare batch input
    batch_inputs = self.input_data[: self.config.batch_size]
    batch_inputs = self.input_data[: self.config.batch_size]
    if len(batch_inputs) < self.config.batch_size:
    if len(batch_inputs) < self.config.batch_size:
    # Repeat inputs to fill the batch
    # Repeat inputs to fill the batch
    batch_inputs = (
    batch_inputs = (
    batch_inputs * (self.config.batch_size // len(batch_inputs) + 1)
    batch_inputs * (self.config.batch_size // len(batch_inputs) + 1)
    )[: self.config.batch_size]
    )[: self.config.batch_size]


    # Tokenize inputs
    # Tokenize inputs
    encoded_inputs = tokenizer(batch_inputs, padding=True, return_tensors="pt")
    encoded_inputs = tokenizer(batch_inputs, padding=True, return_tensors="pt")
    if self.config.device == "cuda" and TORCH_AVAILABLE:
    if self.config.device == "cuda" and TORCH_AVAILABLE:
    encoded_inputs = {k: v.cuda() for k, v in encoded_inputs.items()}
    encoded_inputs = {k: v.cuda() for k, v in encoded_inputs.items()}


    # Count input tokens
    # Count input tokens
    input_token_count = encoded_inputs["input_ids"].numel()
    input_token_count = encoded_inputs["input_ids"].numel()


    # Warmup runs
    # Warmup runs
    for _ in range(self.config.warmup_runs):
    for _ in range(self.config.warmup_runs):
    with torch.no_grad():
    with torch.no_grad():
    if self.config.model_type == "text-generation":
    if self.config.model_type == "text-generation":
    model.generate(**encoded_inputs, max_length=self.config.max_tokens)
    model.generate(**encoded_inputs, max_length=self.config.max_tokens)
    else:
    else:
    model(**encoded_inputs)
    model(**encoded_inputs)


    # Benchmark runs
    # Benchmark runs
    start_time = time.time()
    start_time = time.time()
    total_output_tokens = 0
    total_output_tokens = 0


    for _ in range(self.config.num_runs):
    for _ in range(self.config.num_runs):
    with torch.no_grad():
    with torch.no_grad():
    if self.config.model_type == "text-generation":
    if self.config.model_type == "text-generation":
    outputs = model.generate(
    outputs = model.generate(
    **encoded_inputs, max_length=self.config.max_tokens
    **encoded_inputs, max_length=self.config.max_tokens
    )
    )
    total_output_tokens += outputs.numel()
    total_output_tokens += outputs.numel()
    else:
    else:
    model(**encoded_inputs)
    model(**encoded_inputs)
    total_output_tokens += (
    total_output_tokens += (
    input_token_count  # For non-generative models
    input_token_count  # For non-generative models
    )
    )


    end_time = time.time()
    end_time = time.time()
    total_time = end_time - start_time
    total_time = end_time - start_time


    # Calculate throughput
    # Calculate throughput
    total_tokens = total_output_tokens
    total_tokens = total_output_tokens
    throughput = total_tokens / total_time
    throughput = total_tokens / total_time


    logger.info(f"Throughput: {throughput:.2f} tokens/second")
    logger.info(f"Throughput: {throughput:.2f} tokens/second")
    return throughput
    return throughput


    def _measure_memory(self) -> float:
    def _measure_memory(self) -> float:
    """
    """
    Measure memory usage.
    Measure memory usage.


    Returns:
    Returns:
    Memory usage in MB
    Memory usage in MB
    """
    """
    logger.info("Measuring memory usage...")
    logger.info("Measuring memory usage...")


    # Clear memory before loading model
    # Clear memory before loading model
    if TORCH_AVAILABLE:
    if TORCH_AVAILABLE:
    torch.cuda.empty_cache()
    torch.cuda.empty_cache()
    gc.collect()
    gc.collect()


    # Measure baseline memory
    # Measure baseline memory
    baseline_memory = self._get_memory_usage()
    baseline_memory = self._get_memory_usage()


    # Load model and measure memory
    # Load model and measure memory
    model, tokenizer = self._load_model()
    model, tokenizer = self._load_model()


    # Run inference to ensure model is fully loaded
    # Run inference to ensure model is fully loaded
    self._run_inference(model, tokenizer, self.input_data[0])
    self._run_inference(model, tokenizer, self.input_data[0])


    # Measure memory usage
    # Measure memory usage
    model_memory = self._get_memory_usage()
    model_memory = self._get_memory_usage()


    # Calculate memory usage
    # Calculate memory usage
    memory_usage_mb = model_memory - baseline_memory
    memory_usage_mb = model_memory - baseline_memory


    logger.info(f"Memory usage: {memory_usage_mb:.2f} MB")
    logger.info(f"Memory usage: {memory_usage_mb:.2f} MB")
    return memory_usage_mb
    return memory_usage_mb


    def _get_memory_usage(self) -> float:
    def _get_memory_usage(self) -> float:
    """
    """
    Get current memory usage.
    Get current memory usage.


    Returns:
    Returns:
    Memory usage in MB
    Memory usage in MB
    """
    """
    if self.config.device == "cuda" and TORCH_AVAILABLE:
    if self.config.device == "cuda" and TORCH_AVAILABLE:
    return torch.cuda.memory_allocated() / (1024 * 1024)
    return torch.cuda.memory_allocated() / (1024 * 1024)
    elif PSUTIL_AVAILABLE:
    elif PSUTIL_AVAILABLE:
    return psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024)
    return psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024)
    else:
    else:
    return 0.0
    return 0.0


    def _measure_accuracy(self, reference_file: str) -> float:
    def _measure_accuracy(self, reference_file: str) -> float:
    """
    """
    Measure model accuracy.
    Measure model accuracy.


    Args:
    Args:
    reference_file: Path to reference data
    reference_file: Path to reference data


    Returns:
    Returns:
    Accuracy score
    Accuracy score
    """
    """
    logger.info("Measuring accuracy...")
    logger.info("Measuring accuracy...")


    if not os.path.exists(reference_file):
    if not os.path.exists(reference_file):
    raise FileNotFoundError(f"Reference file not found: {reference_file}")
    raise FileNotFoundError(f"Reference file not found: {reference_file}")


    model, tokenizer = self._load_model()
    model, tokenizer = self._load_model()


    # Load reference data
    # Load reference data
    with open(reference_file, "r") as f:
    with open(reference_file, "r") as f:
    reference_data = json.load(f)
    reference_data = json.load(f)


    if not isinstance(reference_data, list):
    if not isinstance(reference_data, list):
    raise ValueError("Reference data must be a list of input-output pairs")
    raise ValueError("Reference data must be a list of input-output pairs")


    # Run inference and calculate accuracy
    # Run inference and calculate accuracy
    correct = 0
    correct = 0
    total = 0
    total = 0


    for item in reference_data:
    for item in reference_data:
    if isinstance(item, dict) and "input" in item and "output" in item:
    if isinstance(item, dict) and "input" in item and "output" in item:
    input_text = item["input"]
    input_text = item["input"]
    expected_output = item["output"]
    expected_output = item["output"]


    actual_output = self._run_inference(model, tokenizer, input_text)
    actual_output = self._run_inference(model, tokenizer, input_text)


    if self._compare_outputs(actual_output, expected_output):
    if self._compare_outputs(actual_output, expected_output):
    correct += 1
    correct += 1
    total += 1
    total += 1


    accuracy = correct / total if total > 0 else 0.0
    accuracy = correct / total if total > 0 else 0.0
    logger.info(f"Accuracy: {accuracy:.2f}")
    logger.info(f"Accuracy: {accuracy:.2f}")
    return accuracy
    return accuracy


    def _compare_outputs(self, actual: str, expected: str) -> bool:
    def _compare_outputs(self, actual: str, expected: str) -> bool:
    """
    """
    Compare model output with expected output.
    Compare model output with expected output.


    Args:
    Args:
    actual: Actual model output
    actual: Actual model output
    expected: Expected output
    expected: Expected output


    Returns:
    Returns:
    True if outputs match, False otherwise
    True if outputs match, False otherwise
    """
    """
    # Simple exact match
    # Simple exact match
    if actual == expected:
    if actual == expected:
    return True
    return True


    # Normalized match (case-insensitive, whitespace-normalized)
    # Normalized match (case-insensitive, whitespace-normalized)
    actual_norm = " ".join(actual.lower().split())
    actual_norm = " ".join(actual.lower().split())
    expected_norm = " ".join(expected.lower().split())
    expected_norm = " ".join(expected.lower().split())
    if actual_norm == expected_norm:
    if actual_norm == expected_norm:
    return True
    return True


    # Substring match
    # Substring match
    if actual_norm in expected_norm or expected_norm in actual_norm:
    if actual_norm in expected_norm or expected_norm in actual_norm:
    return True
    return True


    return False
    return False


    def _measure_perplexity(self) -> float:
    def _measure_perplexity(self) -> float:
    """
    """
    Measure model perplexity.
    Measure model perplexity.


    Returns:
    Returns:
    Perplexity score
    Perplexity score
    """
    """
    logger.info("Measuring perplexity...")
    logger.info("Measuring perplexity...")


    if not TRANSFORMERS_AVAILABLE:
    if not TRANSFORMERS_AVAILABLE:
    raise ImportError(
    raise ImportError(
    "Transformers library is required for perplexity calculation"
    "Transformers library is required for perplexity calculation"
    )
    )


    model, tokenizer = self._load_model()
    model, tokenizer = self._load_model()


    # Ensure model is in evaluation mode
    # Ensure model is in evaluation mode
    model.eval()
    model.eval()


    # Calculate perplexity for each input
    # Calculate perplexity for each input
    total_loss = 0.0
    total_loss = 0.0
    total_tokens = 0
    total_tokens = 0


    for input_text in self.input_data:
    for input_text in self.input_data:
    inputs = tokenizer(input_text, return_tensors="pt")
    inputs = tokenizer(input_text, return_tensors="pt")
    if self.config.device == "cuda" and TORCH_AVAILABLE:
    if self.config.device == "cuda" and TORCH_AVAILABLE:
    inputs = {k: v.cuda() for k, v in inputs.items()}
    inputs = {k: v.cuda() for k, v in inputs.items()}


    with torch.no_grad():
    with torch.no_grad():
    outputs = model(**inputs, labels=inputs["input_ids"])
    outputs = model(**inputs, labels=inputs["input_ids"])
    loss = outputs.loss.item()
    loss = outputs.loss.item()


    total_loss += loss * inputs["input_ids"].size(1)
    total_loss += loss * inputs["input_ids"].size(1)
    total_tokens += inputs["input_ids"].size(1)
    total_tokens += inputs["input_ids"].size(1)


    # Calculate perplexity
    # Calculate perplexity
    perplexity = torch.exp(torch.tensor(total_loss / total_tokens)).item()
    perplexity = torch.exp(torch.tensor(total_loss / total_tokens)).item()


    logger.info(f"Perplexity: {perplexity:.2f}")
    logger.info(f"Perplexity: {perplexity:.2f}")
    return perplexity
    return perplexity


    def _measure_rouge(self, reference_file: str) -> Dict[str, float]:
    def _measure_rouge(self, reference_file: str) -> Dict[str, float]:
    """
    """
    Measure ROUGE scores.
    Measure ROUGE scores.


    Args:
    Args:
    reference_file: Path to reference data
    reference_file: Path to reference data


    Returns:
    Returns:
    Dictionary of ROUGE scores
    Dictionary of ROUGE scores
    """
    """
    logger.info("Measuring ROUGE scores...")
    logger.info("Measuring ROUGE scores...")


    if not ROUGE_AVAILABLE:
    if not ROUGE_AVAILABLE:
    raise ImportError("rouge_score library is required for ROUGE calculation")
    raise ImportError("rouge_score library is required for ROUGE calculation")


    if not os.path.exists(reference_file):
    if not os.path.exists(reference_file):
    raise FileNotFoundError(f"Reference file not found: {reference_file}")
    raise FileNotFoundError(f"Reference file not found: {reference_file}")


    model, tokenizer = self._load_model()
    model, tokenizer = self._load_model()


    # Load reference data
    # Load reference data
    with open(reference_file, "r") as f:
    with open(reference_file, "r") as f:
    reference_data = json.load(f)
    reference_data = json.load(f)


    if not isinstance(reference_data, list):
    if not isinstance(reference_data, list):
    raise ValueError("Reference data must be a list of input-output pairs")
    raise ValueError("Reference data must be a list of input-output pairs")


    # Initialize ROUGE scorer
    # Initialize ROUGE scorer
    scorer = rouge_scorer.RougeScorer(
    scorer = rouge_scorer.RougeScorer(
    ["rouge1", "rouge2", "rougeL"], use_stemmer=True
    ["rouge1", "rouge2", "rougeL"], use_stemmer=True
    )
    )


    # Calculate ROUGE scores
    # Calculate ROUGE scores
    rouge_scores = {"rouge1": 0.0, "rouge2": 0.0, "rougeL": 0.0}
    rouge_scores = {"rouge1": 0.0, "rouge2": 0.0, "rougeL": 0.0}
    count = 0
    count = 0


    for item in reference_data:
    for item in reference_data:
    if isinstance(item, dict) and "input" in item and "reference" in item:
    if isinstance(item, dict) and "input" in item and "reference" in item:
    input_text = item["input"]
    input_text = item["input"]
    reference = item["reference"]
    reference = item["reference"]


    prediction = self._run_inference(model, tokenizer, input_text)
    prediction = self._run_inference(model, tokenizer, input_text)
    scores = scorer.score(reference, prediction)
    scores = scorer.score(reference, prediction)


    for key in rouge_scores:
    for key in rouge_scores:
    rouge_scores[key] += scores[key].fmeasure
    rouge_scores[key] += scores[key].fmeasure


    count += 1
    count += 1


    # Average scores
    # Average scores
    if count > 0:
    if count > 0:
    for key in rouge_scores:
    for key in rouge_scores:
    rouge_scores[key] /= count
    rouge_scores[key] /= count


    logger.info(f"ROUGE scores: {rouge_scores}")
    logger.info(f"ROUGE scores: {rouge_scores}")
    return rouge_scores
    return rouge_scores


    def run_benchmark(self) -> BenchmarkResult:
    def run_benchmark(self) -> BenchmarkResult:
    """
    """
    Run the benchmark.
    Run the benchmark.


    Returns:
    Returns:
    Benchmark result
    Benchmark result
    """
    """
    logger.info(f"Running {self.config.benchmark_type.value} benchmark...")
    logger.info(f"Running {self.config.benchmark_type.value} benchmark...")


    result = BenchmarkResult(
    result = BenchmarkResult(
    model_id=os.path.basename(self.config.model_path),
    model_id=os.path.basename(self.config.model_path),
    model_type=self.config.model_type,
    model_type=self.config.model_type,
    benchmark_type=self.config.benchmark_type,
    benchmark_type=self.config.benchmark_type,
    device=self.config.device,
    device=self.config.device,
    num_threads=self.config.num_threads,
    num_threads=self.config.num_threads,
    batch_size=self.config.batch_size,
    batch_size=self.config.batch_size,
    )
    )


    try:
    try:
    if self.config.benchmark_type == BenchmarkType.LATENCY:
    if self.config.benchmark_type == BenchmarkType.LATENCY:
    run_times, outputs = self._measure_latency()
    run_times, outputs = self._measure_latency()
    result.run_times = run_times
    result.run_times = run_times
    result.latency_ms = sum(run_times) / len(run_times) if run_times else 0
    result.latency_ms = sum(run_times) / len(run_times) if run_times else 0


    elif self.config.benchmark_type == BenchmarkType.THROUGHPUT:
    elif self.config.benchmark_type == BenchmarkType.THROUGHPUT:
    result.throughput = self._measure_throughput()
    result.throughput = self._measure_throughput()


    elif self.config.benchmark_type == BenchmarkType.MEMORY:
    elif self.config.benchmark_type == BenchmarkType.MEMORY:
    result.memory_usage_mb = self._measure_memory()
    result.memory_usage_mb = self._measure_memory()


    elif self.config.benchmark_type == BenchmarkType.ACCURACY:
    elif self.config.benchmark_type == BenchmarkType.ACCURACY:
    reference_file = self.config.additional_params.get("reference_file")
    reference_file = self.config.additional_params.get("reference_file")
    if not reference_file:
    if not reference_file:
    raise ValueError(
    raise ValueError(
    "Reference file is required for accuracy benchmark"
    "Reference file is required for accuracy benchmark"
    )
    )
    result.accuracy = self._measure_accuracy(reference_file)
    result.accuracy = self._measure_accuracy(reference_file)


    elif self.config.benchmark_type == BenchmarkType.PERPLEXITY:
    elif self.config.benchmark_type == BenchmarkType.PERPLEXITY:
    result.perplexity = self._measure_perplexity()
    result.perplexity = self._measure_perplexity()


    elif self.config.benchmark_type == BenchmarkType.ROUGE:
    elif self.config.benchmark_type == BenchmarkType.ROUGE:
    reference_file = self.config.additional_params.get("reference_file")
    reference_file = self.config.additional_params.get("reference_file")
    if not reference_file:
    if not reference_file:
    raise ValueError("Reference file is required for ROUGE benchmark")
    raise ValueError("Reference file is required for ROUGE benchmark")
    result.rouge_scores = self._measure_rouge(reference_file)
    result.rouge_scores = self._measure_rouge(reference_file)


    elif self.config.benchmark_type == BenchmarkType.CUSTOM:
    elif self.config.benchmark_type == BenchmarkType.CUSTOM:
    custom_benchmark_func = self.config.additional_params.get(
    custom_benchmark_func = self.config.additional_params.get(
    "benchmark_func"
    "benchmark_func"
    )
    )
    if not custom_benchmark_func:
    if not custom_benchmark_func:
    raise ValueError(
    raise ValueError(
    "Custom benchmark function is required for custom benchmark"
    "Custom benchmark function is required for custom benchmark"
    )
    )
    custom_metrics = custom_benchmark_func(self.config, self._load_model)
    custom_metrics = custom_benchmark_func(self.config, self._load_model)
    result.custom_metrics = custom_metrics
    result.custom_metrics = custom_metrics


    else:
    else:
    raise ValueError(
    raise ValueError(
    f"Unsupported benchmark type: {self.config.benchmark_type}"
    f"Unsupported benchmark type: {self.config.benchmark_type}"
    )
    )


except Exception as e:
except Exception as e:
    logger.error(f"Benchmark failed: {str(e)}")
    logger.error(f"Benchmark failed: {str(e)}")
    raise
    raise


    # Save results if requested
    # Save results if requested
    if self.config.save_results and self.config.output_dir:
    if self.config.save_results and self.config.output_dir:
    os.makedirs(self.config.output_dir, exist_ok=True)
    os.makedirs(self.config.output_dir, exist_ok=True)
    output_file = os.path.join(
    output_file = os.path.join(
    self.config.output_dir,
    self.config.output_dir,
    f"{result.model_id}_{result.benchmark_type.value}_{int(time.time())}.json",
    f"{result.model_id}_{result.benchmark_type.value}_{int(time.time())}.json",
    )
    )
    result.save_to_file(output_file)
    result.save_to_file(output_file)
    logger.info(f"Results saved to {output_file}")
    logger.info(f"Results saved to {output_file}")


    return result
    return result




    # Example usage
    # Example usage
    if __name__ == "__main__":
    if __name__ == "__main__":
    # Create a benchmark configuration
    # Create a benchmark configuration
    config = BenchmarkConfig(
    config = BenchmarkConfig(
    model_path="gpt2",
    model_path="gpt2",
    model_type="text-generation",
    model_type="text-generation",
    benchmark_type=BenchmarkType.LATENCY,
    benchmark_type=BenchmarkType.LATENCY,
    device="cpu",
    device="cpu",
    num_runs=5,
    num_runs=5,
    warmup_runs=2,
    warmup_runs=2,
    max_tokens=50,
    max_tokens=50,
    )
    )


    # Create a benchmark runner
    # Create a benchmark runner
    runner = BenchmarkRunner(config)
    runner = BenchmarkRunner(config)


    # Run the benchmark
    # Run the benchmark
    result = runner.run_benchmark()
    result = runner.run_benchmark()


    # Print the results
    # Print the results
    print(f"Model: {result.model_id}")
    print(f"Model: {result.model_id}")
    print(f"Benchmark type: {result.benchmark_type.value}")
    print(f"Benchmark type: {result.benchmark_type.value}")
    print(f"Latency: {result.latency_ms:.2f} ms")
    print(f"Latency: {result.latency_ms:.2f} ms")
    print(f"Run times: {[f'{t:.2f}' for t in result.run_times]}")
    print(f"Run times: {[f'{t:.2f}' for t in result.run_times]}")
    print(f"Device: {result.device}")
    print(f"Device: {result.device}")
    print(f"Batch size: {result.batch_size}")
    print(f"Batch size: {result.batch_size}")
    print(f"Threads: {result.num_threads}")
    print(f"Threads: {result.num_threads}")

