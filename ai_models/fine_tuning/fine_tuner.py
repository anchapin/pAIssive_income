"""
"""
Fine-tuning tools for AI models.
Fine-tuning tools for AI models.


This module provides tools for fine-tuning AI models using various methods
This module provides tools for fine-tuning AI models using various methods
and configurations.
and configurations.
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
    import time
    import time
    from dataclasses import dataclass, field
    from dataclasses import dataclass, field
    from enum import Enum
    from enum import Enum
    from typing import Any, Dict, List, Optional, Union
    from typing import Any, Dict, List, Optional, Union


    import torch
    import torch
    from datasets import Dataset, DatasetDict, load_dataset, load_from_disk
    from datasets import Dataset, DatasetDict, load_dataset, load_from_disk


    (
    (
    LoraConfig,
    LoraConfig,
    PeftConfig,
    PeftConfig,
    TaskType,
    TaskType,
    get_peft_model,
    get_peft_model,
    prepare_model_for_kbit_training,
    prepare_model_for_kbit_training,
    )
    )
    from transformers import (AutoModelForCausalLM, AutoTokenizer,
    from transformers import (AutoModelForCausalLM, AutoTokenizer,
    DataCollatorForLanguageModeling,
    DataCollatorForLanguageModeling,
    EarlyStoppingCallback, Trainer, TrainingArguments)
    EarlyStoppingCallback, Trainer, TrainingArguments)


    # Configure logger
    # Configure logger
    logger = logging.getLogger(__name__)
    logger = logging.getLogger(__name__)




    class FineTuningMethod(Enum):
    class FineTuningMethod(Enum):
    """
    """
    Enum for fine-tuning methods.
    Enum for fine-tuning methods.
    """
    """


    FULL = "full"
    FULL = "full"
    LORA = "lora"
    LORA = "lora"
    QLORA = "qlora"
    QLORA = "qlora"
    PREFIX_TUNING = "prefix_tuning"
    PREFIX_TUNING = "prefix_tuning"
    PROMPT_TUNING = "prompt_tuning"
    PROMPT_TUNING = "prompt_tuning"




    @dataclass
    @dataclass
    class FineTuningConfig:
    class FineTuningConfig:
    """
    """
    Configuration for fine-tuning.
    Configuration for fine-tuning.
    """
    """


    # Model information
    # Model information
    model_path: str
    model_path: str
    output_dir: str
    output_dir: str


    # Fine-tuning method
    # Fine-tuning method
    method: FineTuningMethod = FineTuningMethod.LORA
    method: FineTuningMethod = FineTuningMethod.LORA


    # Dataset information
    # Dataset information
    dataset_path: Optional[str] = None
    dataset_path: Optional[str] = None
    dataset: Optional[Union[Dataset, DatasetDict]] = None
    dataset: Optional[Union[Dataset, DatasetDict]] = None


    # Training parameters
    # Training parameters
    num_train_epochs: int = 3
    num_train_epochs: int = 3
    per_device_train_batch_size: int = 4
    per_device_train_batch_size: int = 4
    per_device_eval_batch_size: int = 4
    per_device_eval_batch_size: int = 4
    gradient_accumulation_steps: int = 1
    gradient_accumulation_steps: int = 1
    learning_rate: float = 5e-5
    learning_rate: float = 5e-5
    weight_decay: float = 0.01
    weight_decay: float = 0.01
    warmup_steps: int = 0
    warmup_steps: int = 0
    max_steps: int = -1
    max_steps: int = -1


    # Evaluation parameters
    # Evaluation parameters
    evaluation_strategy: str = "epoch"
    evaluation_strategy: str = "epoch"
    eval_steps: int = 500
    eval_steps: int = 500
    save_strategy: str = "epoch"
    save_strategy: str = "epoch"
    save_steps: int = 500
    save_steps: int = 500


    # Early stopping
    # Early stopping
    early_stopping_patience: Optional[int] = None
    early_stopping_patience: Optional[int] = None


    # LoRA parameters (for LoRA and QLoRA)
    # LoRA parameters (for LoRA and QLoRA)
    lora_r: int = 8
    lora_r: int = 8
    lora_alpha: int = 16
    lora_alpha: int = 16
    lora_dropout: float = 0.05
    lora_dropout: float = 0.05
    lora_target_modules: List[str] = field(default_factory=lambda: ["q_proj", "v_proj"])
    lora_target_modules: List[str] = field(default_factory=lambda: ["q_proj", "v_proj"])


    # Quantization parameters (for QLoRA)
    # Quantization parameters (for QLoRA)
    quantization_bits: int = 4
    quantization_bits: int = 4


    # Prefix tuning parameters
    # Prefix tuning parameters
    prefix_length: int = 10
    prefix_length: int = 10


    # Prompt tuning parameters
    # Prompt tuning parameters
    prompt_length: int = 10
    prompt_length: int = 10


    # Tokenizer parameters
    # Tokenizer parameters
    max_length: int = 512
    max_length: int = 512


    # Logging parameters
    # Logging parameters
    logging_steps: int = 100
    logging_steps: int = 100


    # Hardware parameters
    # Hardware parameters
    device: str = "auto"
    device: str = "auto"


    # Metadata
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)




    class FineTuner:
    class FineTuner:
    """
    """
    Class for fine-tuning AI models.
    Class for fine-tuning AI models.
    """
    """


    def __init__(self, config: FineTuningConfig):
    def __init__(self, config: FineTuningConfig):
    """
    """
    Initialize the fine-tuner.
    Initialize the fine-tuner.


    Args:
    Args:
    config: Configuration for fine-tuning
    config: Configuration for fine-tuning
    """
    """
    self.config = config
    self.config = config
    self.trainer = None
    self.trainer = None
    self.model = None
    self.model = None
    self.tokenizer = None
    self.tokenizer = None
    self.dataset = None
    self.dataset = None


    # Set device
    # Set device
    if self.config.device == "auto":
    if self.config.device == "auto":
    self.device = "cuda" if torch.cuda.is_available() else "cpu"
    self.device = "cuda" if torch.cuda.is_available() else "cpu"
    else:
    else:
    self.device = self.config.device
    self.device = self.config.device


    logger.info(f"Using device: {self.device}")
    logger.info(f"Using device: {self.device}")


    def prepare(self) -> None:
    def prepare(self) -> None:
    """
    """
    Prepare for fine-tuning by loading the model, tokenizer, and dataset.
    Prepare for fine-tuning by loading the model, tokenizer, and dataset.
    """
    """
    # Load dataset
    # Load dataset
    self._load_dataset()
    self._load_dataset()


    # Load tokenizer
    # Load tokenizer
    self._load_tokenizer()
    self._load_tokenizer()


    # Prepare dataset
    # Prepare dataset
    self._prepare_dataset()
    self._prepare_dataset()


    # Load model
    # Load model
    self._load_model()
    self._load_model()


    # Create trainer
    # Create trainer
    self._create_trainer()
    self._create_trainer()


    def train(self) -> Dict[str, Any]:
    def train(self) -> Dict[str, Any]:
    """
    """
    Train the model.
    Train the model.


    Returns:
    Returns:
    Training metrics
    Training metrics
    """
    """
    if self.trainer is None:
    if self.trainer is None:
    self.prepare()
    self.prepare()


    # Train the model
    # Train the model
    logger.info("Starting training")
    logger.info("Starting training")
    train_result = self.trainer.train()
    train_result = self.trainer.train()


    # Save the model
    # Save the model
    logger.info(f"Saving model to {self.config.output_dir}")
    logger.info(f"Saving model to {self.config.output_dir}")
    self.trainer.save_model()
    self.trainer.save_model()


    # Save tokenizer
    # Save tokenizer
    self.tokenizer.save_pretrained(self.config.output_dir)
    self.tokenizer.save_pretrained(self.config.output_dir)


    # Save training arguments
    # Save training arguments
    with open(os.path.join(self.config.output_dir, "training_args.json"), "w") as f:
    with open(os.path.join(self.config.output_dir, "training_args.json"), "w") as f:
    json.dump(self.trainer.args.to_dict(), f, indent=2)
    json.dump(self.trainer.args.to_dict(), f, indent=2)


    # Save fine-tuning configuration
    # Save fine-tuning configuration
    self._save_config()
    self._save_config()


    # Return metrics
    # Return metrics
    metrics = train_result.metrics
    metrics = train_result.metrics
    logger.info(f"Training metrics: {metrics}")
    logger.info(f"Training metrics: {metrics}")
    return metrics
    return metrics


    def resume(self, checkpoint_dir: Optional[str] = None) -> Dict[str, Any]:
    def resume(self, checkpoint_dir: Optional[str] = None) -> Dict[str, Any]:
    """
    """
    Resume training from a checkpoint.
    Resume training from a checkpoint.


    Args:
    Args:
    checkpoint_dir: Directory containing the checkpoint
    checkpoint_dir: Directory containing the checkpoint


    Returns:
    Returns:
    Training metrics
    Training metrics
    """
    """
    if self.trainer is None:
    if self.trainer is None:
    self.prepare()
    self.prepare()


    # Set checkpoint directory
    # Set checkpoint directory
    if checkpoint_dir is None:
    if checkpoint_dir is None:
    checkpoint_dir = self.config.output_dir
    checkpoint_dir = self.config.output_dir


    # Resume training
    # Resume training
    logger.info(f"Resuming training from {checkpoint_dir}")
    logger.info(f"Resuming training from {checkpoint_dir}")
    train_result = self.trainer.train(resume_from_checkpoint=checkpoint_dir)
    train_result = self.trainer.train(resume_from_checkpoint=checkpoint_dir)


    # Save the model
    # Save the model
    logger.info(f"Saving model to {self.config.output_dir}")
    logger.info(f"Saving model to {self.config.output_dir}")
    self.trainer.save_model()
    self.trainer.save_model()


    # Save tokenizer
    # Save tokenizer
    self.tokenizer.save_pretrained(self.config.output_dir)
    self.tokenizer.save_pretrained(self.config.output_dir)


    # Return metrics
    # Return metrics
    metrics = train_result.metrics
    metrics = train_result.metrics
    logger.info(f"Training metrics: {metrics}")
    logger.info(f"Training metrics: {metrics}")
    return metrics
    return metrics


    def evaluate(self) -> Dict[str, Any]:
    def evaluate(self) -> Dict[str, Any]:
    """
    """
    Evaluate the model.
    Evaluate the model.


    Returns:
    Returns:
    Evaluation metrics
    Evaluation metrics
    """
    """
    if self.trainer is None:
    if self.trainer is None:
    self.prepare()
    self.prepare()


    # Evaluate the model
    # Evaluate the model
    logger.info("Evaluating model")
    logger.info("Evaluating model")
    metrics = self.trainer.evaluate()
    metrics = self.trainer.evaluate()


    logger.info(f"Evaluation metrics: {metrics}")
    logger.info(f"Evaluation metrics: {metrics}")
    return metrics
    return metrics


    def save(self, output_dir: Optional[str] = None) -> str:
    def save(self, output_dir: Optional[str] = None) -> str:
    """
    """
    Save the fine-tuned model.
    Save the fine-tuned model.


    Args:
    Args:
    output_dir: Directory to save the model
    output_dir: Directory to save the model


    Returns:
    Returns:
    Path to the saved model
    Path to the saved model
    """
    """
    if output_dir is None:
    if output_dir is None:
    output_dir = self.config.output_dir
    output_dir = self.config.output_dir


    # Create output directory if it doesn't exist
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)


    # Save the model
    # Save the model
    if self.model is not None:
    if self.model is not None:
    logger.info(f"Saving model to {output_dir}")
    logger.info(f"Saving model to {output_dir}")
    self.model.save_pretrained(output_dir)
    self.model.save_pretrained(output_dir)


    # Save the tokenizer
    # Save the tokenizer
    if self.tokenizer is not None:
    if self.tokenizer is not None:
    logger.info(f"Saving tokenizer to {output_dir}")
    logger.info(f"Saving tokenizer to {output_dir}")
    self.tokenizer.save_pretrained(output_dir)
    self.tokenizer.save_pretrained(output_dir)


    # Save fine-tuning configuration
    # Save fine-tuning configuration
    self._save_config(output_dir)
    self._save_config(output_dir)


    return output_dir
    return output_dir


    def _load_dataset(self) -> None:
    def _load_dataset(self) -> None:
    """
    """
    Load the dataset for fine-tuning.
    Load the dataset for fine-tuning.
    """
    """
    # Check if dataset is provided directly
    # Check if dataset is provided directly
    if self.config.dataset is not None:
    if self.config.dataset is not None:
    self.dataset = self.config.dataset
    self.dataset = self.config.dataset
    logger.info("Using provided dataset")
    logger.info("Using provided dataset")
    return # Check if dataset path is provided
    return # Check if dataset path is provided
    if self.config.dataset_path is None:
    if self.config.dataset_path is None:
    raise ValueError("Either dataset or dataset_path must be provided")
    raise ValueError("Either dataset or dataset_path must be provided")


    # Load dataset based on path
    # Load dataset based on path
    try:
    try:
    # Check if it's a Hugging Face dataset
    # Check if it's a Hugging Face dataset
    if os.path.exists(self.config.dataset_path):
    if os.path.exists(self.config.dataset_path):
    # Check if it's a directory (Hugging Face dataset saved to disk)
    # Check if it's a directory (Hugging Face dataset saved to disk)
    if os.path.isdir(self.config.dataset_path):
    if os.path.isdir(self.config.dataset_path):
    self.dataset = load_from_disk(self.config.dataset_path)
    self.dataset = load_from_disk(self.config.dataset_path)
    # Check if it's a file (JSON, CSV, etc.)
    # Check if it's a file (JSON, CSV, etc.)
    else:
    else:
    _, ext = os.path.splitext(self.config.dataset_path)
    _, ext = os.path.splitext(self.config.dataset_path)
    ext = ext.lower()
    ext = ext.lower()


    if ext == ".jsonl" or ext == ".json":
    if ext == ".jsonl" or ext == ".json":
    self.dataset = load_dataset(
    self.dataset = load_dataset(
    "json", data_files=self.config.dataset_path
    "json", data_files=self.config.dataset_path
    )
    )
    elif ext == ".csv":
    elif ext == ".csv":
    self.dataset = load_dataset(
    self.dataset = load_dataset(
    "csv", data_files=self.config.dataset_path
    "csv", data_files=self.config.dataset_path
    )
    )
    elif ext == ".parquet":
    elif ext == ".parquet":
    self.dataset = load_dataset(
    self.dataset = load_dataset(
    "parquet", data_files=self.config.dataset_path
    "parquet", data_files=self.config.dataset_path
    )
    )
    else:
    else:
    raise ValueError(f"Unsupported file format: {ext}")
    raise ValueError(f"Unsupported file format: {ext}")
    else:
    else:
    # Try to load as a Hugging Face dataset
    # Try to load as a Hugging Face dataset
    self.dataset = load_dataset(self.config.dataset_path)
    self.dataset = load_dataset(self.config.dataset_path)


    logger.info(f"Loaded dataset from {self.config.dataset_path}")
    logger.info(f"Loaded dataset from {self.config.dataset_path}")
except Exception as e:
except Exception as e:
    logger.error(f"Error loading dataset: {e}")
    logger.error(f"Error loading dataset: {e}")
    raise
    raise


    def _load_tokenizer(self) -> None:
    def _load_tokenizer(self) -> None:
    """
    """
    Load the tokenizer for fine-tuning.
    Load the tokenizer for fine-tuning.
    """
    """
    try:
    try:
    self.tokenizer = AutoTokenizer.from_pretrained(self.config.model_path)
    self.tokenizer = AutoTokenizer.from_pretrained(self.config.model_path)


    # Add padding token if it doesn't exist
    # Add padding token if it doesn't exist
    if self.tokenizer.pad_token is None:
    if self.tokenizer.pad_token is None:
    self.tokenizer.pad_token = self.tokenizer.eos_token
    self.tokenizer.pad_token = self.tokenizer.eos_token


    logger.info(f"Loaded tokenizer from {self.config.model_path}")
    logger.info(f"Loaded tokenizer from {self.config.model_path}")
except Exception as e:
except Exception as e:
    logger.error(f"Error loading tokenizer: {e}")
    logger.error(f"Error loading tokenizer: {e}")
    raise
    raise


    def _prepare_dataset(self) -> None:
    def _prepare_dataset(self) -> None:
    """
    """
    Prepare the dataset for fine-tuning.
    Prepare the dataset for fine-tuning.
    """
    """
    if self.dataset is None or self.tokenizer is None:
    if self.dataset is None or self.tokenizer is None:
    raise ValueError(
    raise ValueError(
    "Dataset and tokenizer must be loaded before preparing the dataset"
    "Dataset and tokenizer must be loaded before preparing the dataset"
    )
    )


    # Convert to DatasetDict if it's not already
    # Convert to DatasetDict if it's not already
    if not isinstance(self.dataset, DatasetDict):
    if not isinstance(self.dataset, DatasetDict):
    # Check if it has train/validation splits
    # Check if it has train/validation splits
    if "train" in self.dataset and "validation" in self.dataset:
    if "train" in self.dataset and "validation" in self.dataset:
    self.dataset = DatasetDict(
    self.dataset = DatasetDict(
    {
    {
    "train": self.dataset["train"],
    "train": self.dataset["train"],
    "validation": self.dataset["validation"],
    "validation": self.dataset["validation"],
    }
    }
    )
    )
    else:
    else:
    # Create a validation split
    # Create a validation split
    train_val_split = self.dataset["train"].train_test_split(test_size=0.1)
    train_val_split = self.dataset["train"].train_test_split(test_size=0.1)
    self.dataset = DatasetDict(
    self.dataset = DatasetDict(
    {
    {
    "train": train_val_split["train"],
    "train": train_val_split["train"],
    "validation": train_val_split["test"],
    "validation": train_val_split["test"],
    }
    }
    )
    )


    # Tokenize the dataset
    # Tokenize the dataset
    def tokenize_function(examples):
    def tokenize_function(examples):
    # Find text fields
    # Find text fields
    text_fields = []
    text_fields = []
    for field in ["text", "content", "input", "prompt", "question"]:
    for field in ["text", "content", "input", "prompt", "question"]:
    if field in examples and isinstance(examples[field], list):
    if field in examples and isinstance(examples[field], list):
    text_fields.append(field)
    text_fields.append(field)


    if not text_fields:
    if not text_fields:
    raise ValueError("No text field found in the dataset")
    raise ValueError("No text field found in the dataset")


    # Tokenize each text field
    # Tokenize each text field
    result = {}
    result = {}
    for field in text_fields:
    for field in text_fields:
    tokenized = self.tokenizer(
    tokenized = self.tokenizer(
    examples[field],
    examples[field],
    padding="max_length",
    padding="max_length",
    truncation=True,
    truncation=True,
    max_length=self.config.max_length,
    max_length=self.config.max_length,
    )
    )


    # Add to result with field prefix
    # Add to result with field prefix
    for key, value in tokenized.items():
    for key, value in tokenized.items():
    result[f"{field}_{key}"] = value
    result[f"{field}_{key}"] = value


    return result
    return result


    # Apply tokenization
    # Apply tokenization
    tokenized_dataset = self.dataset.map(
    tokenized_dataset = self.dataset.map(
    tokenize_function,
    tokenize_function,
    batched=True,
    batched=True,
    remove_columns=self.dataset["train"].column_names,
    remove_columns=self.dataset["train"].column_names,
    )
    )


    self.dataset = tokenized_dataset
    self.dataset = tokenized_dataset
    logger.info("Dataset prepared for fine-tuning")
    logger.info("Dataset prepared for fine-tuning")


    def _load_model(self) -> None:
    def _load_model(self) -> None:
    """
    """
    Load the model for fine-tuning.
    Load the model for fine-tuning.
    """
    """
    try:
    try:
    # Load model based on fine-tuning method
    # Load model based on fine-tuning method
    if self.config.method == FineTuningMethod.FULL:
    if self.config.method == FineTuningMethod.FULL:
    self._load_full_model()
    self._load_full_model()
    elif self.config.method == FineTuningMethod.LORA:
    elif self.config.method == FineTuningMethod.LORA:
    self._load_lora_model()
    self._load_lora_model()
    elif self.config.method == FineTuningMethod.QLORA:
    elif self.config.method == FineTuningMethod.QLORA:
    self._load_qlora_model()
    self._load_qlora_model()
    elif self.config.method == FineTuningMethod.PREFIX_TUNING:
    elif self.config.method == FineTuningMethod.PREFIX_TUNING:
    self._load_prefix_tuning_model()
    self._load_prefix_tuning_model()
    elif self.config.method == FineTuningMethod.PROMPT_TUNING:
    elif self.config.method == FineTuningMethod.PROMPT_TUNING:
    self._load_prompt_tuning_model()
    self._load_prompt_tuning_model()
    else:
    else:
    raise ValueError(
    raise ValueError(
    f"Unsupported fine-tuning method: {self.config.method}"
    f"Unsupported fine-tuning method: {self.config.method}"
    )
    )


    logger.info(
    logger.info(
    f"Loaded model from {self.config.model_path} using {self.config.method.value} method"
    f"Loaded model from {self.config.model_path} using {self.config.method.value} method"
    )
    )
except Exception as e:
except Exception as e:
    logger.error(f"Error loading model: {e}")
    logger.error(f"Error loading model: {e}")
    raise
    raise


    def _load_full_model(self) -> None:
    def _load_full_model(self) -> None:
    """
    """
    Load the model for full fine-tuning.
    Load the model for full fine-tuning.
    """
    """
    self.model = AutoModelForCausalLM.from_pretrained(
    self.model = AutoModelForCausalLM.from_pretrained(
    self.config.model_path, device_map=self.device
    self.config.model_path, device_map=self.device
    )
    )


    def _load_lora_model(self) -> None:
    def _load_lora_model(self) -> None:
    """
    """
    Load the model for LoRA fine-tuning.
    Load the model for LoRA fine-tuning.
    """
    """
    # Load base model
    # Load base model
    self.model = AutoModelForCausalLM.from_pretrained(
    self.model = AutoModelForCausalLM.from_pretrained(
    self.config.model_path, device_map=self.device
    self.config.model_path, device_map=self.device
    )
    )


    # Create LoRA configuration
    # Create LoRA configuration
    lora_config = LoraConfig(
    lora_config = LoraConfig(
    r=self.config.lora_r,
    r=self.config.lora_r,
    lora_alpha=self.config.lora_alpha,
    lora_alpha=self.config.lora_alpha,
    target_modules=self.config.lora_target_modules,
    target_modules=self.config.lora_target_modules,
    lora_dropout=self.config.lora_dropout,
    lora_dropout=self.config.lora_dropout,
    bias="none",
    bias="none",
    task_type=TaskType.CAUSAL_LM,
    task_type=TaskType.CAUSAL_LM,
    )
    )


    # Apply LoRA
    # Apply LoRA
    self.model = get_peft_model(self.model, lora_config)
    self.model = get_peft_model(self.model, lora_config)


    def _load_qlora_model(self) -> None:
    def _load_qlora_model(self) -> None:
    """
    """
    Load the model for QLoRA fine-tuning.
    Load the model for QLoRA fine-tuning.
    """
    """
    # Load base model with quantization
    # Load base model with quantization
    self.model = AutoModelForCausalLM.from_pretrained(
    self.model = AutoModelForCausalLM.from_pretrained(
    self.config.model_path,
    self.config.model_path,
    device_map=self.device,
    device_map=self.device,
    load_in_4bit=self.config.quantization_bits == 4,
    load_in_4bit=self.config.quantization_bits == 4,
    load_in_8bit=self.config.quantization_bits == 8,
    load_in_8bit=self.config.quantization_bits == 8,
    )
    )


    # Prepare model for k-bit training
    # Prepare model for k-bit training
    self.model = prepare_model_for_kbit_training(self.model)
    self.model = prepare_model_for_kbit_training(self.model)


    # Create LoRA configuration
    # Create LoRA configuration
    lora_config = LoraConfig(
    lora_config = LoraConfig(
    r=self.config.lora_r,
    r=self.config.lora_r,
    lora_alpha=self.config.lora_alpha,
    lora_alpha=self.config.lora_alpha,
    target_modules=self.config.lora_target_modules,
    target_modules=self.config.lora_target_modules,
    lora_dropout=self.config.lora_dropout,
    lora_dropout=self.config.lora_dropout,
    bias="none",
    bias="none",
    task_type=TaskType.CAUSAL_LM,
    task_type=TaskType.CAUSAL_LM,
    )
    )


    # Apply LoRA
    # Apply LoRA
    self.model = get_peft_model(self.model, lora_config)
    self.model = get_peft_model(self.model, lora_config)


    def _load_prefix_tuning_model(self) -> None:
    def _load_prefix_tuning_model(self) -> None:
    """
    """
    Load the model for prefix tuning.
    Load the model for prefix tuning.
    """
    """
    # Load base model
    # Load base model
    self.model = AutoModelForCausalLM.from_pretrained(
    self.model = AutoModelForCausalLM.from_pretrained(
    self.config.model_path, device_map=self.device
    self.config.model_path, device_map=self.device
    )
    )


    # Create prefix tuning configuration
    # Create prefix tuning configuration
    prefix_config = PeftConfig(
    prefix_config = PeftConfig(
    task_type=TaskType.CAUSAL_LM,
    task_type=TaskType.CAUSAL_LM,
    inference_mode=False,
    inference_mode=False,
    num_virtual_tokens=self.config.prefix_length,
    num_virtual_tokens=self.config.prefix_length,
    )
    )


    # Apply prefix tuning
    # Apply prefix tuning
    self.model = get_peft_model(self.model, prefix_config)
    self.model = get_peft_model(self.model, prefix_config)


    def _load_prompt_tuning_model(self) -> None:
    def _load_prompt_tuning_model(self) -> None:
    """
    """
    Load the model for prompt tuning.
    Load the model for prompt tuning.
    """
    """
    # Load base model
    # Load base model
    self.model = AutoModelForCausalLM.from_pretrained(
    self.model = AutoModelForCausalLM.from_pretrained(
    self.config.model_path, device_map=self.device
    self.config.model_path, device_map=self.device
    )
    )


    # Create prompt tuning configuration
    # Create prompt tuning configuration
    prompt_config = PeftConfig(
    prompt_config = PeftConfig(
    task_type=TaskType.CAUSAL_LM,
    task_type=TaskType.CAUSAL_LM,
    inference_mode=False,
    inference_mode=False,
    num_virtual_tokens=self.config.prompt_length,
    num_virtual_tokens=self.config.prompt_length,
    )
    )


    # Apply prompt tuning
    # Apply prompt tuning
    self.model = get_peft_model(self.model, prompt_config)
    self.model = get_peft_model(self.model, prompt_config)


    def _create_trainer(self) -> None:
    def _create_trainer(self) -> None:
    """
    """
    Create the trainer for fine-tuning.
    Create the trainer for fine-tuning.
    """
    """
    if self.model is None or self.dataset is None:
    if self.model is None or self.dataset is None:
    raise ValueError(
    raise ValueError(
    "Model and dataset must be loaded before creating the trainer"
    "Model and dataset must be loaded before creating the trainer"
    )
    )


    # Create training arguments
    # Create training arguments
    training_args = TrainingArguments(
    training_args = TrainingArguments(
    output_dir=self.config.output_dir,
    output_dir=self.config.output_dir,
    num_train_epochs=self.config.num_train_epochs,
    num_train_epochs=self.config.num_train_epochs,
    per_device_train_batch_size=self.config.per_device_train_batch_size,
    per_device_train_batch_size=self.config.per_device_train_batch_size,
    per_device_eval_batch_size=self.config.per_device_eval_batch_size,
    per_device_eval_batch_size=self.config.per_device_eval_batch_size,
    gradient_accumulation_steps=self.config.gradient_accumulation_steps,
    gradient_accumulation_steps=self.config.gradient_accumulation_steps,
    learning_rate=self.config.learning_rate,
    learning_rate=self.config.learning_rate,
    weight_decay=self.config.weight_decay,
    weight_decay=self.config.weight_decay,
    warmup_steps=self.config.warmup_steps,
    warmup_steps=self.config.warmup_steps,
    max_steps=self.config.max_steps,
    max_steps=self.config.max_steps,
    evaluation_strategy=self.config.evaluation_strategy,
    evaluation_strategy=self.config.evaluation_strategy,
    eval_steps=self.config.eval_steps,
    eval_steps=self.config.eval_steps,
    save_strategy=self.config.save_strategy,
    save_strategy=self.config.save_strategy,
    save_steps=self.config.save_steps,
    save_steps=self.config.save_steps,
    logging_steps=self.config.logging_steps,
    logging_steps=self.config.logging_steps,
    save_total_limit=2,
    save_total_limit=2,
    load_best_model_at_end=True,
    load_best_model_at_end=True,
    report_to="none",
    report_to="none",
    )
    )


    # Create data collator
    # Create data collator
    data_collator = DataCollatorForLanguageModeling(
    data_collator = DataCollatorForLanguageModeling(
    tokenizer=self.tokenizer, mlm=False
    tokenizer=self.tokenizer, mlm=False
    )
    )


    # Create callbacks
    # Create callbacks
    callbacks = []
    callbacks = []


    # Add early stopping if configured
    # Add early stopping if configured
    if self.config.early_stopping_patience is not None:
    if self.config.early_stopping_patience is not None:
    callbacks.append(
    callbacks.append(
    EarlyStoppingCallback(
    EarlyStoppingCallback(
    early_stopping_patience=self.config.early_stopping_patience
    early_stopping_patience=self.config.early_stopping_patience
    )
    )
    )
    )


    # Create trainer
    # Create trainer
    self.trainer = Trainer(
    self.trainer = Trainer(
    model=self.model,
    model=self.model,
    args=training_args,
    args=training_args,
    train_dataset=self.dataset["train"],
    train_dataset=self.dataset["train"],
    eval_dataset=self.dataset["validation"],
    eval_dataset=self.dataset["validation"],
    data_collator=data_collator,
    data_collator=data_collator,
    tokenizer=self.tokenizer,
    tokenizer=self.tokenizer,
    callbacks=callbacks,
    callbacks=callbacks,
    )
    )


    def _save_config(self, output_dir: Optional[str] = None) -> None:
    def _save_config(self, output_dir: Optional[str] = None) -> None:
    """
    """
    Save the fine-tuning configuration.
    Save the fine-tuning configuration.


    Args:
    Args:
    output_dir: Directory to save the configuration
    output_dir: Directory to save the configuration
    """
    """
    if output_dir is None:
    if output_dir is None:
    output_dir = self.config.output_dir
    output_dir = self.config.output_dir


    # Create output directory if it doesn't exist
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)


    # Convert config to dictionary
    # Convert config to dictionary
    config_dict = {
    config_dict = {
    "model_path": self.config.model_path,
    "model_path": self.config.model_path,
    "output_dir": self.config.output_dir,
    "output_dir": self.config.output_dir,
    "method": self.config.method.value,
    "method": self.config.method.value,
    "dataset_path": self.config.dataset_path,
    "dataset_path": self.config.dataset_path,
    "num_train_epochs": self.config.num_train_epochs,
    "num_train_epochs": self.config.num_train_epochs,
    "per_device_train_batch_size": self.config.per_device_train_batch_size,
    "per_device_train_batch_size": self.config.per_device_train_batch_size,
    "per_device_eval_batch_size": self.config.per_device_eval_batch_size,
    "per_device_eval_batch_size": self.config.per_device_eval_batch_size,
    "gradient_accumulation_steps": self.config.gradient_accumulation_steps,
    "gradient_accumulation_steps": self.config.gradient_accumulation_steps,
    "learning_rate": self.config.learning_rate,
    "learning_rate": self.config.learning_rate,
    "weight_decay": self.config.weight_decay,
    "weight_decay": self.config.weight_decay,
    "warmup_steps": self.config.warmup_steps,
    "warmup_steps": self.config.warmup_steps,
    "max_steps": self.config.max_steps,
    "max_steps": self.config.max_steps,
    "evaluation_strategy": self.config.evaluation_strategy,
    "evaluation_strategy": self.config.evaluation_strategy,
    "eval_steps": self.config.eval_steps,
    "eval_steps": self.config.eval_steps,
    "save_strategy": self.config.save_strategy,
    "save_strategy": self.config.save_strategy,
    "save_steps": self.config.save_steps,
    "save_steps": self.config.save_steps,
    "early_stopping_patience": self.config.early_stopping_patience,
    "early_stopping_patience": self.config.early_stopping_patience,
    "lora_r": self.config.lora_r,
    "lora_r": self.config.lora_r,
    "lora_alpha": self.config.lora_alpha,
    "lora_alpha": self.config.lora_alpha,
    "lora_dropout": self.config.lora_dropout,
    "lora_dropout": self.config.lora_dropout,
    "lora_target_modules": self.config.lora_target_modules,
    "lora_target_modules": self.config.lora_target_modules,
    "quantization_bits": self.config.quantization_bits,
    "quantization_bits": self.config.quantization_bits,
    "prefix_length": self.config.prefix_length,
    "prefix_length": self.config.prefix_length,
    "prompt_length": self.config.prompt_length,
    "prompt_length": self.config.prompt_length,
    "max_length": self.config.max_length,
    "max_length": self.config.max_length,
    "logging_steps": self.config.logging_steps,
    "logging_steps": self.config.logging_steps,
    "device": self.config.device,
    "device": self.config.device,
    "metadata": self.config.metadata,
    "metadata": self.config.metadata,
    }
    }


    # Save configuration
    # Save configuration
    config_path = os.path.join(output_dir, "fine_tuning_config.json")
    config_path = os.path.join(output_dir, "fine_tuning_config.json")
    with open(config_path, "w", encoding="utf-8") as f:
    with open(config_path, "w", encoding="utf-8") as f:
    json.dump(config_dict, f, indent=2)
    json.dump(config_dict, f, indent=2)




    def fine_tune_model(config: FineTuningConfig) -> str:
    def fine_tune_model(config: FineTuningConfig) -> str:
    """
    """
    Fine-tune a model.
    Fine-tune a model.


    Args:
    Args:
    config: Configuration for fine-tuning
    config: Configuration for fine-tuning


    Returns:
    Returns:
    Path to the fine-tuned model
    Path to the fine-tuned model
    """
    """
    # Create fine-tuner
    # Create fine-tuner
    fine_tuner = FineTuner(config)
    fine_tuner = FineTuner(config)


    # Prepare for fine-tuning
    # Prepare for fine-tuning
    fine_tuner.prepare()
    fine_tuner.prepare()


    # Train the model
    # Train the model
    fine_tuner.train()
    fine_tuner.train()


    # Save the model
    # Save the model
    output_path = fine_tuner.save()
    output_path = fine_tuner.save()


    return output_path
    return output_path




    def resume_fine_tuning(output_dir: str, checkpoint_dir: Optional[str] = None) -> str:
    def resume_fine_tuning(output_dir: str, checkpoint_dir: Optional[str] = None) -> str:
    """
    """
    Resume fine-tuning from a checkpoint.
    Resume fine-tuning from a checkpoint.


    Args:
    Args:
    output_dir: Directory containing the fine-tuning configuration
    output_dir: Directory containing the fine-tuning configuration
    checkpoint_dir: Directory containing the checkpoint
    checkpoint_dir: Directory containing the checkpoint


    Returns:
    Returns:
    Path to the fine-tuned model
    Path to the fine-tuned model
    """
    """
    # Load configuration
    # Load configuration
    config_path = os.path.join(output_dir, "fine_tuning_config.json")
    config_path = os.path.join(output_dir, "fine_tuning_config.json")
    if not os.path.exists(config_path):
    if not os.path.exists(config_path):
    raise ValueError(f"Fine-tuning configuration not found at {config_path}")
    raise ValueError(f"Fine-tuning configuration not found at {config_path}")


    with open(config_path, "r", encoding="utf-8") as f:
    with open(config_path, "r", encoding="utf-8") as f:
    config_dict = json.load(f)
    config_dict = json.load(f)


    # Convert method to enum
    # Convert method to enum
    method = config_dict.get("method", "lora")
    method = config_dict.get("method", "lora")
    try:
    try:
    method = FineTuningMethod(method)
    method = FineTuningMethod(method)
except ValueError:
except ValueError:
    method = FineTuningMethod.LORA
    method = FineTuningMethod.LORA


    # Create configuration
    # Create configuration
    config = FineTuningConfig(
    config = FineTuningConfig(
    model_path=config_dict.get("model_path"),
    model_path=config_dict.get("model_path"),
    output_dir=output_dir,
    output_dir=output_dir,
    method=method,
    method=method,
    dataset_path=config_dict.get("dataset_path"),
    dataset_path=config_dict.get("dataset_path"),
    num_train_epochs=config_dict.get("num_train_epochs", 3),
    num_train_epochs=config_dict.get("num_train_epochs", 3),
    per_device_train_batch_size=config_dict.get("per_device_train_batch_size", 4),
    per_device_train_batch_size=config_dict.get("per_device_train_batch_size", 4),
    per_device_eval_batch_size=config_dict.get("per_device_eval_batch_size", 4),
    per_device_eval_batch_size=config_dict.get("per_device_eval_batch_size", 4),
    gradient_accumulation_steps=config_dict.get("gradient_accumulation_steps", 1),
    gradient_accumulation_steps=config_dict.get("gradient_accumulation_steps", 1),
    learning_rate=config_dict.get("learning_rate", 5e-5),
    learning_rate=config_dict.get("learning_rate", 5e-5),
    weight_decay=config_dict.get("weight_decay", 0.01),
    weight_decay=config_dict.get("weight_decay", 0.01),
    warmup_steps=config_dict.get("warmup_steps", 0),
    warmup_steps=config_dict.get("warmup_steps", 0),
    max_steps=config_dict.get("max_steps", -1),
    max_steps=config_dict.get("max_steps", -1),
    evaluation_strategy=config_dict.get("evaluation_strategy", "epoch"),
    evaluation_strategy=config_dict.get("evaluation_strategy", "epoch"),
    eval_steps=config_dict.get("eval_steps", 500),
    eval_steps=config_dict.get("eval_steps", 500),
    save_strategy=config_dict.get("save_strategy", "epoch"),
    save_strategy=config_dict.get("save_strategy", "epoch"),
    save_steps=config_dict.get("save_steps", 500),
    save_steps=config_dict.get("save_steps", 500),
    early_stopping_patience=config_dict.get("early_stopping_patience"),
    early_stopping_patience=config_dict.get("early_stopping_patience"),
    lora_r=config_dict.get("lora_r", 8),
    lora_r=config_dict.get("lora_r", 8),
    lora_alpha=config_dict.get("lora_alpha", 16),
    lora_alpha=config_dict.get("lora_alpha", 16),
    lora_dropout=config_dict.get("lora_dropout", 0.05),
    lora_dropout=config_dict.get("lora_dropout", 0.05),
    lora_target_modules=config_dict.get(
    lora_target_modules=config_dict.get(
    "lora_target_modules", ["q_proj", "v_proj"]
    "lora_target_modules", ["q_proj", "v_proj"]
    ),
    ),
    quantization_bits=config_dict.get("quantization_bits", 4),
    quantization_bits=config_dict.get("quantization_bits", 4),
    prefix_length=config_dict.get("prefix_length", 10),
    prefix_length=config_dict.get("prefix_length", 10),
    prompt_length=config_dict.get("prompt_length", 10),
    prompt_length=config_dict.get("prompt_length", 10),
    max_length=config_dict.get("max_length", 512),
    max_length=config_dict.get("max_length", 512),
    logging_steps=config_dict.get("logging_steps", 100),
    logging_steps=config_dict.get("logging_steps", 100),
    device=config_dict.get("device", "auto"),
    device=config_dict.get("device", "auto"),
    metadata=config_dict.get("metadata", {}),
    metadata=config_dict.get("metadata", {}),
    )
    )


    # Create fine-tuner
    # Create fine-tuner
    fine_tuner = FineTuner(config)
    fine_tuner = FineTuner(config)


    # Prepare for fine-tuning
    # Prepare for fine-tuning
    fine_tuner.prepare()
    fine_tuner.prepare()


    # Resume training
    # Resume training
    fine_tuner.resume(checkpoint_dir)
    fine_tuner.resume(checkpoint_dir)


    # Save the model
    # Save the model
    output_path = fine_tuner.save()
    output_path = fine_tuner.save()


    return output_path
    return output_path




    def stop_fine_tuning(output_dir: str) -> bool:
    def stop_fine_tuning(output_dir: str) -> bool:
    """
    """
    Stop fine-tuning by creating a stop file.
    Stop fine-tuning by creating a stop file.


    Args:
    Args:
    output_dir: Directory containing the fine-tuning process
    output_dir: Directory containing the fine-tuning process


    Returns:
    Returns:
    True if the stop file was created, False otherwise
    True if the stop file was created, False otherwise
    """
    """
    try:
    try:
    # Create stop file
    # Create stop file
    stop_file = os.path.join(output_dir, "stop_fine_tuning")
    stop_file = os.path.join(output_dir, "stop_fine_tuning")
    with open(stop_file, "w") as f:
    with open(stop_file, "w") as f:
    f.write(f"Stop requested at {time.strftime('%Y-%m-%d %H:%M:%S')}")
    f.write(f"Stop requested at {time.strftime('%Y-%m-%d %H:%M:%S')}")


    return True
    return True
except Exception as e:
except Exception as e:
    logger.error(f"Error creating stop file: {e}")
    logger.error(f"Error creating stop file: {e}")
    return False
    return False