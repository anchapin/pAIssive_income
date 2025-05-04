"""
Benchmark runner for AI models.

This module provides functionality for running benchmarks on AI models.
"""

import gc
import json
import logging
import os
import time
from typing import Any, Dict, List, Tuple

from .benchmark_config import BenchmarkConfig, BenchmarkType
from .benchmark_result import BenchmarkResult

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
    logger.warning("PyTorch not available. Some benchmarks may not work.")
    TORCH_AVAILABLE = False

    try:
    import transformers

    TRANSFORMERS_AVAILABLE = True
except ImportError:
    logger.warning("Transformers not available. Some benchmarks may not work.")
    TRANSFORMERS_AVAILABLE = False

    try:
    import psutil

    PSUTIL_AVAILABLE = True
except ImportError:
    logger.warning("psutil not available. Memory benchmarks will be limited.")
    PSUTIL_AVAILABLE = False

    try:
    import numpy as np

    NUMPY_AVAILABLE = True
except ImportError:
    logger.warning("NumPy not available. Some benchmarks may not work.")
    NUMPY_AVAILABLE = False

    try:
    from rouge_score import rouge_scorer

    ROUGE_AVAILABLE = True
except ImportError:
    logger.warning("rouge_score not available. ROUGE benchmarks will not work.")
    ROUGE_AVAILABLE = False


    class BenchmarkRunner:
    """
    Runner for benchmarking AI models.
    """

    def __init__(self, config: BenchmarkConfig):
    """
    Initialize the benchmark runner.

    Args:
    config: Benchmark configuration
    """
    self.config = config
    self.model = None
    self.tokenizer = None
    self.input_data = self._load_input_data()

    def _load_input_data(self) -> List[str]:
    """
    Load input data for benchmarking.

    Returns:
    List of input strings
    """
    if self.config.input_data:
    if isinstance(self.config.input_data, list):
    return self.config.input_data
    else:
    return [self.config.input_data]
    elif self.config.input_file:
    if not os.path.exists(self.config.input_file):
    raise FileNotFoundError(
    f"Input file not found: {self.config.input_file}"
    )

    with open(self.config.input_file, "r") as f:
    if self.config.input_file.endswith(".json"):
    data = json.load(f)
    if isinstance(data, list):
    return data
    else:
    return [json.dumps(data)]
    else:
    return f.read().splitlines()
    else:
    # Default input data
    return [
    "Hello, world!",
    "How are you today?",
    "What is the meaning of life?",
    ]

    def _load_model(self) -> Tuple[Any, Any]:
    """
    Load the model for benchmarking.

    Returns:
    Tuple of (model, tokenizer)
    """
    if self.config.model_type == "text-generation":
    if not TRANSFORMERS_AVAILABLE:
    raise ImportError(
    "Transformers library is required for text generation models"
    )

    logger.info(f"Loading model: {self.config.model_path}")
    tokenizer = transformers.AutoTokenizer.from_pretrained(
    self.config.model_path
    )
    model = transformers.AutoModelForCausalLM.from_pretrained(
    self.config.model_path,
    device_map=self.config.device if self.config.device != "cpu" else None,
    torch_dtype=torch.float16 if self.config.device == "cuda" else None,
    )
    return model, tokenizer

    elif self.config.model_type == "embedding":
    if not TRANSFORMERS_AVAILABLE:
    raise ImportError(
    "Transformers library is required for embedding models"
    )

    logger.info(f"Loading model: {self.config.model_path}")
    tokenizer = transformers.AutoTokenizer.from_pretrained(
    self.config.model_path
    )
    model = transformers.AutoModel.from_pretrained(
    self.config.model_path,
    device_map=self.config.device if self.config.device != "cpu" else None,
    torch_dtype=torch.float16 if self.config.device == "cuda" else None,
    )
    return model, tokenizer

    else:
    raise ValueError(f"Unsupported model type: {self.config.model_type}")

    def _run_inference(self, model: Any, tokenizer: Any, input_text: str) -> Any:
    """
    Run inference with the model.

    Args:
    model: The model to use
    tokenizer: The tokenizer to use
    input_text: Input text for inference

    Returns:
    Model output
    """
    if self.config.model_type == "text-generation":
    inputs = tokenizer(input_text, return_tensors="pt")
    if self.config.device == "cuda" and TORCH_AVAILABLE:
    inputs = {k: v.cuda() for k, v in inputs.items()}

    with torch.no_grad():
    outputs = model.generate(
    **inputs,
    max_length=self.config.max_tokens,
    **self.config.additional_params,
    )

    return tokenizer.decode(outputs[0], skip_special_tokens=True)

    elif self.config.model_type == "embedding":
    inputs = tokenizer(
    input_text, return_tensors="pt", padding=True, truncation=True
    )
    if self.config.device == "cuda" and TORCH_AVAILABLE:
    inputs = {k: v.cuda() for k, v in inputs.items()}

    with torch.no_grad():
    outputs = model(**inputs)

    # Get embeddings from the last hidden state
    embeddings = outputs.last_hidden_state.mean(dim=1)
    return embeddings.cpu().numpy() if TORCH_AVAILABLE else embeddings.numpy()

    else:
    raise ValueError(f"Unsupported model type: {self.config.model_type}")

    def _measure_latency(self) -> Tuple[List[float], List[Any]]:
    """
    Measure inference latency.

    Returns:
    Tuple of (run times in ms, outputs)
    """
    logger.info("Measuring inference latency...")

    model, tokenizer = self._load_model()
    run_times = []
    outputs = []

    # Warmup runs
    for _ in range(self.config.warmup_runs):
    self._run_inference(model, tokenizer, self.input_data[0])

    # Benchmark runs
    for i in range(min(self.config.num_runs, len(self.input_data))):
    input_text = self.input_data[i % len(self.input_data)]

    start_time = time.time()
    output = self._run_inference(model, tokenizer, input_text)
    end_time = time.time()

    run_time_ms = (end_time - start_time) * 1000
    run_times.append(run_time_ms)
    outputs.append(output)

    logger.info(f"Run {i+1}/{self.config.num_runs}: {run_time_ms:.2f} ms")

    return run_times, outputs

    def _measure_throughput(self) -> float:
    """
    Measure inference throughput.

    Returns:
    Throughput in tokens per second
    """
    logger.info("Measuring inference throughput...")

    model, tokenizer = self._load_model()

    # Prepare batch input
    batch_inputs = self.input_data[: self.config.batch_size]
    if len(batch_inputs) < self.config.batch_size:
    # Repeat inputs to fill the batch
    batch_inputs = (
    batch_inputs * (self.config.batch_size // len(batch_inputs) + 1)
    )[: self.config.batch_size]

    # Tokenize inputs
    encoded_inputs = tokenizer(batch_inputs, padding=True, return_tensors="pt")
    if self.config.device == "cuda" and TORCH_AVAILABLE:
    encoded_inputs = {k: v.cuda() for k, v in encoded_inputs.items()}

    # Count input tokens
    input_token_count = encoded_inputs["input_ids"].numel()

    # Warmup runs
    for _ in range(self.config.warmup_runs):
    with torch.no_grad():
    if self.config.model_type == "text-generation":
    model.generate(**encoded_inputs, max_length=self.config.max_tokens)
    else:
    model(**encoded_inputs)

    # Benchmark runs
    start_time = time.time()
    total_output_tokens = 0

    for _ in range(self.config.num_runs):
    with torch.no_grad():
    if self.config.model_type == "text-generation":
    outputs = model.generate(
    **encoded_inputs, max_length=self.config.max_tokens
    )
    total_output_tokens += outputs.numel()
    else:
    model(**encoded_inputs)
    total_output_tokens += (
    input_token_count  # For non-generative models
    )

    end_time = time.time()
    total_time = end_time - start_time

    # Calculate throughput
    total_tokens = total_output_tokens
    throughput = total_tokens / total_time

    logger.info(f"Throughput: {throughput:.2f} tokens/second")
    return throughput

    def _measure_memory(self) -> float:
    """
    Measure memory usage.

    Returns:
    Memory usage in MB
    """
    logger.info("Measuring memory usage...")

    # Clear memory before loading model
    if TORCH_AVAILABLE:
    torch.cuda.empty_cache()
    gc.collect()

    # Measure baseline memory
    baseline_memory = self._get_memory_usage()

    # Load model and measure memory
    model, tokenizer = self._load_model()

    # Run inference to ensure model is fully loaded
    self._run_inference(model, tokenizer, self.input_data[0])

    # Measure memory usage
    model_memory = self._get_memory_usage()

    # Calculate memory usage
    memory_usage_mb = model_memory - baseline_memory

    logger.info(f"Memory usage: {memory_usage_mb:.2f} MB")
    return memory_usage_mb

    def _get_memory_usage(self) -> float:
    """
    Get current memory usage.

    Returns:
    Memory usage in MB
    """
    if self.config.device == "cuda" and TORCH_AVAILABLE:
    return torch.cuda.memory_allocated() / (1024 * 1024)
    elif PSUTIL_AVAILABLE:
    return psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024)
    else:
    return 0.0

    def _measure_accuracy(self, reference_file: str) -> float:
    """
    Measure model accuracy.

    Args:
    reference_file: Path to reference data

    Returns:
    Accuracy score
    """
    logger.info("Measuring accuracy...")

    if not os.path.exists(reference_file):
    raise FileNotFoundError(f"Reference file not found: {reference_file}")

    model, tokenizer = self._load_model()

    # Load reference data
    with open(reference_file, "r") as f:
    reference_data = json.load(f)

    if not isinstance(reference_data, list):
    raise ValueError("Reference data must be a list of input-output pairs")

    # Run inference and calculate accuracy
    correct = 0
    total = 0

    for item in reference_data:
    if isinstance(item, dict) and "input" in item and "output" in item:
    input_text = item["input"]
    expected_output = item["output"]

    actual_output = self._run_inference(model, tokenizer, input_text)

    if self._compare_outputs(actual_output, expected_output):
    correct += 1
    total += 1

    accuracy = correct / total if total > 0 else 0.0
    logger.info(f"Accuracy: {accuracy:.2f}")
    return accuracy

    def _compare_outputs(self, actual: str, expected: str) -> bool:
    """
    Compare model output with expected output.

    Args:
    actual: Actual model output
    expected: Expected output

    Returns:
    True if outputs match, False otherwise
    """
    # Simple exact match
    if actual == expected:
    return True

    # Normalized match (case-insensitive, whitespace-normalized)
    actual_norm = " ".join(actual.lower().split())
    expected_norm = " ".join(expected.lower().split())
    if actual_norm == expected_norm:
    return True

    # Substring match
    if actual_norm in expected_norm or expected_norm in actual_norm:
    return True

    return False

    def _measure_perplexity(self) -> float:
    """
    Measure model perplexity.

    Returns:
    Perplexity score
    """
    logger.info("Measuring perplexity...")

    if not TRANSFORMERS_AVAILABLE:
    raise ImportError(
    "Transformers library is required for perplexity calculation"
    )

    model, tokenizer = self._load_model()

    # Ensure model is in evaluation mode
    model.eval()

    # Calculate perplexity for each input
    total_loss = 0.0
    total_tokens = 0

    for input_text in self.input_data:
    inputs = tokenizer(input_text, return_tensors="pt")
    if self.config.device == "cuda" and TORCH_AVAILABLE:
    inputs = {k: v.cuda() for k, v in inputs.items()}

    with torch.no_grad():
    outputs = model(**inputs, labels=inputs["input_ids"])
    loss = outputs.loss.item()

    total_loss += loss * inputs["input_ids"].size(1)
    total_tokens += inputs["input_ids"].size(1)

    # Calculate perplexity
    perplexity = torch.exp(torch.tensor(total_loss / total_tokens)).item()

    logger.info(f"Perplexity: {perplexity:.2f}")
    return perplexity

    def _measure_rouge(self, reference_file: str) -> Dict[str, float]:
    """
    Measure ROUGE scores.

    Args:
    reference_file: Path to reference data

    Returns:
    Dictionary of ROUGE scores
    """
    logger.info("Measuring ROUGE scores...")

    if not ROUGE_AVAILABLE:
    raise ImportError("rouge_score library is required for ROUGE calculation")

    if not os.path.exists(reference_file):
    raise FileNotFoundError(f"Reference file not found: {reference_file}")

    model, tokenizer = self._load_model()

    # Load reference data
    with open(reference_file, "r") as f:
    reference_data = json.load(f)

    if not isinstance(reference_data, list):
    raise ValueError("Reference data must be a list of input-output pairs")

    # Initialize ROUGE scorer
    scorer = rouge_scorer.RougeScorer(
    ["rouge1", "rouge2", "rougeL"], use_stemmer=True
    )

    # Calculate ROUGE scores
    rouge_scores = {"rouge1": 0.0, "rouge2": 0.0, "rougeL": 0.0}
    count = 0

    for item in reference_data:
    if isinstance(item, dict) and "input" in item and "reference" in item:
    input_text = item["input"]
    reference = item["reference"]

    prediction = self._run_inference(model, tokenizer, input_text)
    scores = scorer.score(reference, prediction)

    for key in rouge_scores:
    rouge_scores[key] += scores[key].fmeasure

    count += 1

    # Average scores
    if count > 0:
    for key in rouge_scores:
    rouge_scores[key] /= count

    logger.info(f"ROUGE scores: {rouge_scores}")
    return rouge_scores

    def run_benchmark(self) -> BenchmarkResult:
    """
    Run the benchmark.

    Returns:
    Benchmark result
    """
    logger.info(f"Running {self.config.benchmark_type.value} benchmark...")

    result = BenchmarkResult(
    model_id=os.path.basename(self.config.model_path),
    model_type=self.config.model_type,
    benchmark_type=self.config.benchmark_type,
    device=self.config.device,
    num_threads=self.config.num_threads,
    batch_size=self.config.batch_size,
    )

    try:
    if self.config.benchmark_type == BenchmarkType.LATENCY:
    run_times, outputs = self._measure_latency()
    result.run_times = run_times
    result.latency_ms = sum(run_times) / len(run_times) if run_times else 0

    elif self.config.benchmark_type == BenchmarkType.THROUGHPUT:
    result.throughput = self._measure_throughput()

    elif self.config.benchmark_type == BenchmarkType.MEMORY:
    result.memory_usage_mb = self._measure_memory()

    elif self.config.benchmark_type == BenchmarkType.ACCURACY:
    reference_file = self.config.additional_params.get("reference_file")
    if not reference_file:
    raise ValueError(
    "Reference file is required for accuracy benchmark"
    )
    result.accuracy = self._measure_accuracy(reference_file)

    elif self.config.benchmark_type == BenchmarkType.PERPLEXITY:
    result.perplexity = self._measure_perplexity()

    elif self.config.benchmark_type == BenchmarkType.ROUGE:
    reference_file = self.config.additional_params.get("reference_file")
    if not reference_file:
    raise ValueError("Reference file is required for ROUGE benchmark")
    result.rouge_scores = self._measure_rouge(reference_file)

    elif self.config.benchmark_type == BenchmarkType.CUSTOM:
    custom_benchmark_func = self.config.additional_params.get(
    "benchmark_func"
    )
    if not custom_benchmark_func:
    raise ValueError(
    "Custom benchmark function is required for custom benchmark"
    )
    custom_metrics = custom_benchmark_func(self.config, self._load_model)
    result.custom_metrics = custom_metrics

    else:
    raise ValueError(
    f"Unsupported benchmark type: {self.config.benchmark_type}"
    )

except Exception as e:
    logger.error(f"Benchmark failed: {str(e)}")
    raise

    # Save results if requested
    if self.config.save_results and self.config.output_dir:
    os.makedirs(self.config.output_dir, exist_ok=True)
    output_file = os.path.join(
    self.config.output_dir,
    f"{result.model_id}_{result.benchmark_type.value}_{int(time.time())}.json",
    )
    result.save_to_file(output_file)
    logger.info(f"Results saved to {output_file}")

    return result


    # Example usage
    if __name__ == "__main__":
    # Create a benchmark configuration
    config = BenchmarkConfig(
    model_path="gpt2",
    model_type="text-generation",
    benchmark_type=BenchmarkType.LATENCY,
    device="cpu",
    num_runs=5,
    warmup_runs=2,
    max_tokens=50,
    )

    # Create a benchmark runner
    runner = BenchmarkRunner(config)

    # Run the benchmark
    result = runner.run_benchmark()

    # Print the results
    print(f"Model: {result.model_id}")
    print(f"Benchmark type: {result.benchmark_type.value}")
    print(f"Latency: {result.latency_ms:.2f} ms")
    print(f"Run times: {[f'{t:.2f}' for t in result.run_times]}")
    print(f"Device: {result.device}")
    print(f"Batch size: {result.batch_size}")
    print(f"Threads: {result.num_threads}")
