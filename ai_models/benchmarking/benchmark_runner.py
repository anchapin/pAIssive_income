"""
Benchmark runner for AI models.

This module provides a runner for benchmarking AI models.
"""

import gc
import json
import logging
import os
import time
from typing import List, Tuple

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
    logger.warning("PyTorch not available. Some benchmarks will not work.")
    TORCH_AVAILABLE = False

try:
    import transformers

    TRANSFORMERS_AVAILABLE = True
except ImportError:
    logger.warning("Transformers not available. Some benchmarks will not work.")
    TRANSFORMERS_AVAILABLE = False

try:
    import psutil

    PSUTIL_AVAILABLE = True
except ImportError:
    logger.warning("psutil not available. Memory benchmarks will not work.")
    PSUTIL_AVAILABLE = False

try:
    pass

    NUMPY_AVAILABLE = True
except ImportError:
    logger.warning("NumPy not available. Some benchmarks will not work.")
    NUMPY_AVAILABLE = False


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
        self.result = None

        # Validate configuration
        self._validate_config()

        # Set up device
        self._setup_device()

        # Load input data
        self._load_input_data()

    def _validate_config(self) -> None:
        """
        Validate the benchmark configuration.

        Raises:
            ValueError: If the configuration is invalid
        """
        if not self.config.model_path:
            raise ValueError("Model path is required")

        if self.config.benchmark_type == BenchmarkType.LATENCY:
            if self.config.num_runs < 1:
                raise ValueError("Number of runs must be positive")

        if self.config.benchmark_type == BenchmarkType.THROUGHPUT:
            if self.config.batch_size < 1:
                raise ValueError("Batch size must be positive")

        if self.config.benchmark_type == BenchmarkType.MEMORY:
            if not PSUTIL_AVAILABLE:
                raise ValueError("psutil is required for memory benchmarks")

    def _setup_device(self) -> None:
        """
        Set up the device for benchmarking.
        """
        if not TORCH_AVAILABLE:
            logger.warning("PyTorch not available. Using CPU for benchmarks.")
            self.device = "cpu"
            return

        if self.config.device == "cuda" and not torch.cuda.is_available():
            logger.warning("CUDA not available. Using CPU for benchmarks.")
            self.device = "cpu"
        else:
            self.device = self.config.device

        # Set number of threads
        if self.device == "cpu":
            torch.set_num_threads(self.config.num_threads)

    def _load_input_data(self) -> None:
        """
        Load input data for benchmarking.
        """
        # If input data is provided directly, use it
        if self.config.input_data is not None:
            if isinstance(self.config.input_data, str):
                self.input_data = [self.config.input_data]
            else:
                self.input_data = self.config.input_data

            # Limit to num_samples
            self.input_data = self.input_data[: self.config.num_samples]
            return

        # If input file is provided, load it
        if self.config.input_file is not None:
            if not os.path.exists(self.config.input_file):
                raise ValueError(f"Input file not found: {self.config.input_file}")

            # Load input file
            with open(self.config.input_file, "r", encoding="utf-8") as f:
                if self.config.input_file.endswith(".json"):
                    data = json.load(f)
                    if isinstance(data, list):
                        self.input_data = data
                    else:
                        self.input_data = [data]
                else:
                    self.input_data = [line.strip() for line in f if line.strip()]

            # Limit to num_samples
            self.input_data = self.input_data[: self.config.num_samples]
            return

        # If no input data is provided, use default prompts
        self.input_data = [
            "Once upon a time in a land far away,",
            "The quick brown fox jumps over the lazy dog.",
            "In a shocking turn of events, scientists discovered that",
            "The best way to learn a new programming language is to",
            "If I could travel anywhere in the world, I would go to",
        ]

        # Duplicate if needed
        while len(self.input_data) < self.config.num_samples:
            self.input_data.append(self.input_data[len(self.input_data) % len(self.input_data)])

        # Limit to num_samples
        self.input_data = self.input_data[: self.config.num_samples]

    def run(self) -> BenchmarkResult:
        """
        Run the benchmark.

        Returns:
            Benchmark result
        """
        logger.info(
            f"Running {self.config.benchmark_type.value} benchmark for {self.config.model_path}"
        )

        # Create result object
        self.result = BenchmarkResult(
            model_path=self.config.model_path,
            model_type=self.config.model_type,
            benchmark_type=self.config.benchmark_type,
            config=self.config,
        )

        # Run benchmark based on type
        if self.config.benchmark_type == BenchmarkType.LATENCY:
            self._run_latency_benchmark()
        elif self.config.benchmark_type == BenchmarkType.THROUGHPUT:
            self._run_throughput_benchmark()
        elif self.config.benchmark_type == BenchmarkType.MEMORY:
            self._run_memory_benchmark()
        elif self.config.benchmark_type == BenchmarkType.ACCURACY:
            self._run_accuracy_benchmark()
        elif self.config.benchmark_type == BenchmarkType.PERPLEXITY:
            self._run_perplexity_benchmark()
        elif self.config.benchmark_type == BenchmarkType.ROUGE:
            self._run_rouge_benchmark()
        else:
            logger.warning(f"Unsupported benchmark type: {self.config.benchmark_type}")

        # Save results if requested
        if self.config.save_results and self.config.output_dir:
            os.makedirs(self.config.output_dir, exist_ok=True)
            output_path = os.path.join(
                self.config.output_dir,
                f"{os.path.basename(self.config.model_path)}_{self.config.benchmark_type.value}_{int(time.time())}.json",
            )
            self.result.save(output_path)
            logger.info(f"Saved benchmark results to {output_path}")

        return self.result

    def _run_latency_benchmark(self) -> None:
        """
        Run a latency benchmark.
        """
        if not TRANSFORMERS_AVAILABLE:
            raise ValueError("Transformers is required for latency benchmarks")

        # Load model and tokenizer
        logger.info("Loading model and tokenizer")
        tokenizer = transformers.AutoTokenizer.from_pretrained(self.config.model_path)
        model = self._load_model()

        # Warm up
        logger.info(f"Warming up with {self.config.warmup_runs} runs")
        for _ in range(self.config.warmup_runs):
            prompt = self.input_data[0]
            self._generate_text(model, tokenizer, prompt)

        # Run benchmark
        logger.info(f"Running benchmark with {self.config.num_runs} runs")
        latency_ms = []

        for i in range(self.config.num_runs):
            # Get prompt
            prompt_idx = i % len(self.input_data)
            prompt = self.input_data[prompt_idx]

            # Measure latency
            start_time = time.time()
            self._generate_text(model, tokenizer, prompt)
            end_time = time.time()

            # Calculate latency in milliseconds
            latency = (end_time - start_time) * 1000
            latency_ms.append(latency)

            logger.info(f"Run {i + 1}/{self.config.num_runs}: {latency:.2f} ms")

        # Save results
        self.result.latency_ms = latency_ms

    def _run_throughput_benchmark(self) -> None:
        """
        Run a throughput benchmark.
        """
        if not TRANSFORMERS_AVAILABLE:
            raise ValueError("Transformers is required for throughput benchmarks")

        # Load model and tokenizer
        logger.info("Loading model and tokenizer")
        tokenizer = transformers.AutoTokenizer.from_pretrained(self.config.model_path)
        model = self._load_model()

        # Warm up
        logger.info(f"Warming up with {self.config.warmup_runs} runs")
        for _ in range(self.config.warmup_runs):
            prompts = self.input_data[: self.config.batch_size]
            self._generate_batch(model, tokenizer, prompts)

        # Run benchmark
        logger.info(f"Running throughput benchmark with batch size {self.config.batch_size}")
        total_tokens = 0
        total_time = 0

        for i in range(0, len(self.input_data), self.config.batch_size):
            # Get batch
            batch = self.input_data[i : i + self.config.batch_size]

            # Measure throughput
            start_time = time.time()
            outputs = self._generate_batch(model, tokenizer, batch)
            end_time = time.time()

            # Calculate tokens
            for output in outputs:
                total_tokens += len(tokenizer.encode(output))

            # Calculate time
            batch_time = end_time - start_time
            total_time += batch_time

            logger.info(
                f"Batch {i // self.config.batch_size + 1}: {len(batch)} samples, {batch_time:.2f} seconds"
            )

        # Calculate throughput (tokens per second)
        throughput = total_tokens / total_time if total_time > 0 else 0

        # Save results
        self.result.throughput = throughput
        logger.info(f"Throughput: {throughput:.2f} tokens/second")

    def _run_memory_benchmark(self) -> None:
        """
        Run a memory benchmark.
        """
        if not TRANSFORMERS_AVAILABLE:
            raise ValueError("Transformers is required for memory benchmarks")

        if not PSUTIL_AVAILABLE:
            raise ValueError("psutil is required for memory benchmarks")

        # Get initial memory usage
        initial_memory = self._get_memory_usage()

        # Load model and tokenizer
        logger.info("Loading model and tokenizer")
        tokenizer = transformers.AutoTokenizer.from_pretrained(self.config.model_path)

        # Get memory usage after loading tokenizer
        tokenizer_memory = self._get_memory_usage()

        # Load model
        model = self._load_model()

        # Get memory usage after loading model
        model_memory = self._get_memory_usage()

        # Run inference
        logger.info("Running inference")
        prompt = self.input_data[0]
        self._generate_text(model, tokenizer, prompt)

        # Get memory usage after inference
        inference_memory = self._get_memory_usage()

        # Calculate memory usage
        memory_usage = {
            "initial_mb": initial_memory,
            "tokenizer_mb": tokenizer_memory - initial_memory,
            "model_mb": model_memory - tokenizer_memory,
            "inference_mb": inference_memory - model_memory,
            "total_mb": inference_memory,
        }

        # Save results
        self.result.memory_usage_mb = memory_usage
        logger.info(f"Memory usage: {memory_usage}")

    def _run_accuracy_benchmark(self) -> None:
        """
        Run an accuracy benchmark.
        """
        if not TRANSFORMERS_AVAILABLE:
            raise ValueError("Transformers is required for accuracy benchmarks")

        # Check if input data contains labels
        has_labels = False
        for item in self.input_data:
            if isinstance(item, dict) and "text" in item and "label" in item:
                has_labels = True
                break

        if not has_labels:
            raise ValueError(
                "Input data must contain text and label fields for accuracy benchmarks"
            )

        # Load model and tokenizer
        logger.info("Loading model and tokenizer")
        tokenizer = transformers.AutoTokenizer.from_pretrained(self.config.model_path)
        model = self._load_model()

        # Run benchmark
        logger.info(f"Running accuracy benchmark with {len(self.input_data)} samples")
        correct = 0
        total = 0

        for item in self.input_data:
            if not isinstance(item, dict) or "text" not in item or "label" not in item:
                continue

            # Get text and label
            text = item["text"]
            label = item["label"]

            # Predict
            prediction = self._classify_text(model, tokenizer, text)

            # Check if correct
            if prediction == label:
                correct += 1

            total += 1

        # Calculate accuracy
        accuracy = correct / total if total > 0 else 0

        # Save results
        self.result.accuracy = accuracy
        logger.info(f"Accuracy: {accuracy:.4f} ({correct}/{total})")

    def _run_perplexity_benchmark(self) -> None:
        """
        Run a perplexity benchmark.
        """
        if not TRANSFORMERS_AVAILABLE:
            raise ValueError("Transformers is required for perplexity benchmarks")

        # Load model and tokenizer
        logger.info("Loading model and tokenizer")
        tokenizer = transformers.AutoTokenizer.from_pretrained(self.config.model_path)
        model = self._load_model()

        # Run benchmark
        logger.info(f"Running perplexity benchmark with {len(self.input_data)} samples")
        total_loss = 0
        total_tokens = 0

        for text in self.input_data:
            # Calculate perplexity
            loss, num_tokens = self._calculate_perplexity(model, tokenizer, text)

            total_loss += loss * num_tokens
            total_tokens += num_tokens

        # Calculate average perplexity
        perplexity = (
            torch.exp(total_loss / total_tokens).item() if total_tokens > 0 else float("inf")
        )

        # Save results
        self.result.perplexity = perplexity
        logger.info(f"Perplexity: {perplexity:.4f}")

    def _run_rouge_benchmark(self) -> None:
        """
        Run a ROUGE benchmark.
        """
        try:
            from rouge_score import rouge_scorer
        except ImportError:
            raise ValueError("rouge_score is required for ROUGE benchmarks")

        # Check if input data contains references
        has_references = False
        for item in self.input_data:
            if isinstance(item, dict) and "text" in item and "reference" in item:
                has_references = True
                break

        if not has_references:
            raise ValueError(
                "Input data must contain text and reference fields for ROUGE benchmarks"
            )

        # Load model and tokenizer
        logger.info("Loading model and tokenizer")
        tokenizer = transformers.AutoTokenizer.from_pretrained(self.config.model_path)
        model = self._load_model()

        # Create ROUGE scorer
        scorer = rouge_scorer.RougeScorer(["rouge1", "rouge2", "rougeL"], use_stemmer=True)

        # Run benchmark
        logger.info(f"Running ROUGE benchmark with {len(self.input_data)} samples")
        rouge1_scores = []
        rouge2_scores = []
        rougeL_scores = []

        for item in self.input_data:
            if not isinstance(item, dict) or "text" not in item or "reference" not in item:
                continue

            # Get text and reference
            text = item["text"]
            reference = item["reference"]

            # Generate summary
            summary = self._generate_text(model, tokenizer, text)

            # Calculate ROUGE scores
            scores = scorer.score(reference, summary)

            rouge1_scores.append(scores["rouge1"].fmeasure)
            rouge2_scores.append(scores["rouge2"].fmeasure)
            rougeL_scores.append(scores["rougeL"].fmeasure)

        # Calculate average ROUGE scores
        rouge_scores = {
            "rouge1": sum(rouge1_scores) / len(rouge1_scores) if rouge1_scores else 0,
            "rouge2": sum(rouge2_scores) / len(rouge2_scores) if rouge2_scores else 0,
            "rougeL": sum(rougeL_scores) / len(rougeL_scores) if rougeL_scores else 0,
        }

        # Save results
        self.result.rouge_scores = rouge_scores
        logger.info(f"ROUGE scores: {rouge_scores}")

    def _load_model(self):
        """
        Load a model for benchmarking.

        Returns:
            Loaded model
        """
        # Clear cache
        if TORCH_AVAILABLE and self.device == "cuda":
            torch.cuda.empty_cache()

        gc.collect()

        # Load model based on type
        if self.config.model_type == "text-generation":
            model = transformers.AutoModelForCausalLM.from_pretrained(
                self.config.model_path, device_map=self.device
            )
        elif self.config.model_type == "text-classification":
            model = transformers.AutoModelForSequenceClassification.from_pretrained(
                self.config.model_path, device_map=self.device
            )
        elif self.config.model_type == "embedding":
            model = transformers.AutoModel.from_pretrained(
                self.config.model_path, device_map=self.device
            )
        else:
            raise ValueError(f"Unsupported model type: {self.config.model_type}")

        return model

    def _generate_text(self, model, tokenizer, prompt: str) -> str:
        """
        Generate text using a model.

        Args:
            model: Model to use
            tokenizer: Tokenizer to use
            prompt: Input prompt

        Returns:
            Generated text
        """
        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

        # Set generation parameters
        generation_kwargs = {
            "max_new_tokens": self.config.max_tokens,
            "temperature": 0.7,
            "top_p": 0.9,
            "do_sample": True,
        }

        # Update with additional parameters
        if "generation_kwargs" in self.config.additional_params:
            generation_kwargs.update(self.config.additional_params["generation_kwargs"])

        # Generate
        with torch.no_grad():
            outputs = model.generate(**inputs, **generation_kwargs)

        return tokenizer.decode(outputs[0], skip_special_tokens=True)

    def _generate_batch(self, model, tokenizer, prompts: List[str]) -> List[str]:
        """
        Generate text for a batch of prompts.

        Args:
            model: Model to use
            tokenizer: Tokenizer to use
            prompts: List of input prompts

        Returns:
            List of generated texts
        """
        # Tokenize batch
        batch_inputs = tokenizer(prompts, padding=True, return_tensors="pt").to(model.device)

        # Set generation parameters
        generation_kwargs = {
            "max_new_tokens": self.config.max_tokens,
            "temperature": 0.7,
            "top_p": 0.9,
            "do_sample": True,
        }

        # Update with additional parameters
        if "generation_kwargs" in self.config.additional_params:
            generation_kwargs.update(self.config.additional_params["generation_kwargs"])

        # Generate
        with torch.no_grad():
            outputs = model.generate(**batch_inputs, **generation_kwargs)

        # Decode outputs
        return [tokenizer.decode(output, skip_special_tokens=True) for output in outputs]

    def _classify_text(self, model, tokenizer, text: str) -> str:
        """
        Classify text using a model.

        Args:
            model: Model to use
            tokenizer: Tokenizer to use
            text: Input text

        Returns:
            Predicted label
        """
        inputs = tokenizer(text, return_tensors="pt").to(model.device)

        # Get predictions
        with torch.no_grad():
            outputs = model(**inputs)

        # Get predicted class
        predicted_class = outputs.logits.argmax(-1).item()

        # Convert to label
        if hasattr(model.config, "id2label"):
            return model.config.id2label[predicted_class]
        else:
            return str(predicted_class)

    def _calculate_perplexity(self, model, tokenizer, text: str) -> Tuple[float, int]:
        """
        Calculate perplexity for a text.

        Args:
            model: Model to use
            tokenizer: Tokenizer to use
            text: Input text

        Returns:
            Tuple of (loss, number of tokens)
        """
        # Tokenize input
        encodings = tokenizer(text, return_tensors="pt")
        input_ids = encodings.input_ids.to(model.device)

        # Calculate loss
        with torch.no_grad():
            outputs = model(input_ids, labels=input_ids)
            loss = outputs.loss

        # Get number of tokens
        num_tokens = input_ids.numel()

        return loss.item(), num_tokens

    def _get_memory_usage(self) -> float:
        """
        Get current memory usage.

        Returns:
            Memory usage in megabytes
        """
        # Get process memory usage
        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()

        # Convert to megabytes
        memory_mb = memory_info.rss / (1024 * 1024)

        # Get GPU memory usage if available
        if TORCH_AVAILABLE and self.device == "cuda" and torch.cuda.is_available():
            gpu_memory = torch.cuda.memory_allocated() / (1024 * 1024)
            memory_mb += gpu_memory

        return memory_mb
