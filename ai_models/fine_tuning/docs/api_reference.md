# Fine-Tuning API Reference

This document provides detailed API documentation for the fine-tuning module in the pAIssive_income project.

## Table of Contents

- [Data Collection](#data-collection)
- [Fine-Tuning](#fine-tuning)
- [Evaluation](#evaluation)
- [Workflows](#workflows)

## Data Collection

### Classes

#### `DatasetFormat`

Enum for dataset formats.

```python
class DatasetFormat(Enum):
    JSONL = "jsonl"
    CSV = "csv"
    PARQUET = "parquet"
    HUGGINGFACE = "huggingface"
    CUSTOM = "custom"
```

#### `DataCollectionConfig`

Configuration for data collection.

```python
@dataclass
class DataCollectionConfig:
    # Dataset sources
    sources: List[str] = field(default_factory=list)

    # Output format
    output_format: DatasetFormat = DatasetFormat.JSONL

    # Output path
    output_path: Optional[str] = None

    # Data processing options
    shuffle: bool = True
    max_samples: Optional[int] = None

    # Filtering options
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    filter_function: Optional[Callable[[Dict[str, Any]], bool]] = None

    # Transformation options
    transform_function: Optional[Callable[[Dict[str, Any]], Dict[str, Any]]] = None

    # Validation options
    validation_split: float = 0.1
    test_split: float = 0.1

    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
```

#### `DataCollector`

Class for collecting and preparing datasets for fine-tuning.

```python
class DataCollector:
    def __init__(self, config: DataCollectionConfig):
        """
        Initialize the data collector.

        Args:
            config: Configuration for data collection
        """

    def collect(self) -> Dataset:
        """
        Collect data from the specified sources.

        Returns:
            Collected dataset
        """

    def prepare(self) -> DatasetDict:
        """
        Prepare the dataset for fine-tuning, including train/validation/test splits.

        Returns:
            Prepared dataset with train, validation, and test splits
        """

    def export(self, dataset: Union[Dataset, DatasetDict]) -> str:
        """
        Export the dataset to the specified format.

        Args:
            dataset: Dataset to export

        Returns:
            Path to the exported dataset
        """
```

### Functions

#### `collect_data`

Collect data for fine-tuning.

```python
def collect_data(config: DataCollectionConfig) -> Dataset:
    """
    Collect data for fine-tuning.

    Args:
        config: Configuration for data collection

    Returns:
        Collected dataset
    """
```

#### `prepare_dataset`

Prepare a dataset for fine-tuning.

```python
def prepare_dataset(config: DataCollectionConfig) -> DatasetDict:
    """
    Prepare a dataset for fine-tuning.

    Args:
        config: Configuration for data collection

    Returns:
        Prepared dataset with train, validation, and test splits
    """
```

#### `export_dataset`

Export a dataset to the specified format.

```python
def export_dataset(
    dataset: Union[Dataset, DatasetDict],
    output_path: str,
    format: Union[str, DatasetFormat] = DatasetFormat.JSONL,
    metadata: Optional[Dict[str, Any]] = None
) -> str:
    """
    Export a dataset to the specified format.

    Args:
        dataset: Dataset to export
        output_path: Path for the output
        format: Output format
        metadata: Metadata to include

    Returns:
        Path to the exported dataset
    """
```

## Fine-Tuning

### Classes

#### `FineTuningMethod`

Enum for fine-tuning methods.

```python
class FineTuningMethod(Enum):
    FULL = "full"
    LORA = "lora"
    QLORA = "qlora"
    PREFIX_TUNING = "prefix_tuning"
    PROMPT_TUNING = "prompt_tuning"
```

#### `FineTuningConfig`

Configuration for fine-tuning.

```python
@dataclass
class FineTuningConfig:
    # Model information
    model_path: str
    output_dir: str

    # Fine-tuning method
    method: FineTuningMethod = FineTuningMethod.LORA

    # Dataset information
    dataset_path: Optional[str] = None
    dataset: Optional[Union[Dataset, DatasetDict]] = None

    # Training parameters
    num_train_epochs: int = 3
    per_device_train_batch_size: int = 4
    per_device_eval_batch_size: int = 4
    gradient_accumulation_steps: int = 1
    learning_rate: float = 5e-5
    weight_decay: float = 0.01
    warmup_steps: int = 0
    max_steps: int = -1

    # Evaluation parameters
    evaluation_strategy: str = "epoch"
    eval_steps: int = 500
    save_strategy: str = "epoch"
    save_steps: int = 500

    # Early stopping
    early_stopping_patience: Optional[int] = None

    # LoRA parameters
    lora_r: int = 8
    lora_alpha: int = 16
    lora_dropout: float = 0.05
    lora_target_modules: List[str] = field(default_factory=lambda: ["q_proj", "v_proj"])

    # QLoRA parameters
    quantization_bits: int = 4

    # Prefix tuning parameters
    prefix_length: int = 10

    # Prompt tuning parameters
    prompt_length: int = 10

    # Other parameters
    max_length: int = 512
    logging_steps: int = 100
    device: str = "auto"

    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
```

#### `FineTuner`

Class for fine-tuning AI models.

```python
class FineTuner:
    def __init__(self, config: FineTuningConfig):
        """
        Initialize the fine-tuner.

        Args:
            config: Configuration for fine-tuning
        """

    def prepare(self) -> None:
        """
        Prepare for fine-tuning by loading the model, tokenizer, and dataset.
        """

    def train(self) -> Dict[str, Any]:
        """
        Train the model.

        Returns:
            Training metrics
        """

    def resume(self, checkpoint_dir: Optional[str] = None) -> Dict[str, Any]:
        """
        Resume training from a checkpoint.

        Args:
            checkpoint_dir: Directory containing the checkpoint

        Returns:
            Training metrics
        """

    def evaluate(self) -> Dict[str, Any]:
        """
        Evaluate the model.

        Returns:
            Evaluation metrics
        """

    def save(self, output_dir: Optional[str] = None) -> str:
        """
        Save the fine-tuned model.

        Args:
            output_dir: Directory to save the model

        Returns:
            Path to the saved model
        """
```

### Functions

#### `fine_tune_model`

Fine-tune a model.

```python
def fine_tune_model(config: FineTuningConfig) -> str:
    """
    Fine-tune a model.

    Args:
        config: Configuration for fine-tuning

    Returns:
        Path to the fine-tuned model
    """
```

#### `resume_fine_tuning`

Resume fine-tuning from a checkpoint.

```python
def resume_fine_tuning(
    output_dir: str,
    checkpoint_dir: Optional[str] = None
) -> str:
    """
    Resume fine-tuning from a checkpoint.

    Args:
        output_dir: Directory containing the fine-tuning configuration
        checkpoint_dir: Directory containing the checkpoint

    Returns:
        Path to the fine-tuned model
    """
```

#### `stop_fine_tuning`

Stop fine-tuning by creating a stop file.

```python
def stop_fine_tuning(output_dir: str) -> bool:
    """
    Stop fine-tuning by creating a stop file.

    Args:
        output_dir: Directory containing the fine-tuning process

    Returns:
        True if the stop file was created, False otherwise
    """
```

## Evaluation

### Classes

#### `EvaluationMetric`

Enum for evaluation metrics.

```python
class EvaluationMetric(Enum):
    ACCURACY = "accuracy"
    PERPLEXITY = "perplexity"
    ROUGE = "rouge"
    BLEU = "bleu"
    F1 = "f1"
    EXACT_MATCH = "exact_match"
    CUSTOM = "custom"
```

#### `EvaluationConfig`

Configuration for model evaluation.

```python
@dataclass
class EvaluationConfig:
    # Model information
    model_path: str

    # Dataset information
    dataset_path: Optional[str] = None
    dataset: Optional[Union[Dataset, DatasetDict]] = None

    # Evaluation metrics
    metrics: List[EvaluationMetric] = field(default_factory=lambda: [EvaluationMetric.PERPLEXITY])

    # Custom evaluation function
    custom_evaluation_function: Optional[Callable] = None

    # Output configuration
    output_dir: Optional[str] = None
    save_results: bool = True

    # Evaluation parameters
    batch_size: int = 8
    max_length: int = 512
    num_samples: Optional[int] = None

    # Device configuration
    device: str = "auto"

    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
```

#### `ModelEvaluator`

Class for evaluating fine-tuned models.

```python
class ModelEvaluator:
    def __init__(self, config: EvaluationConfig):
        """
        Initialize the model evaluator.

        Args:
            config: Configuration for evaluation
        """

    def prepare(self) -> None:
        """
        Prepare for evaluation by loading the model, tokenizer, and dataset.
        """

    def evaluate(self) -> Dict[str, Any]:
        """
        Evaluate the model using the configured metrics.

        Returns:
            Dictionary with evaluation results
        """

    def visualize_results(self, output_path: Optional[str] = None) -> str:
        """
        Visualize evaluation results.

        Args:
            output_path: Path to save the visualization

        Returns:
            Path to the saved visualization
        """

    @staticmethod
    def compare_models(
        model_paths: List[str],
        dataset_path: str,
        metrics: List[Union[str, EvaluationMetric]] = None,
        output_dir: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Dict[str, Any]]:
        """
        Compare multiple models using the same evaluation metrics.

        Args:
            model_paths: List of paths to the models
            dataset_path: Path to the dataset
            metrics: List of metrics to use for evaluation
            output_dir: Directory to save the results
            **kwargs: Additional parameters for evaluation

        Returns:
            Dictionary with evaluation results for each model
        """

    @staticmethod
    def visualize_comparison(
        results: Dict[str, Dict[str, Any]],
        output_dir: str
    ) -> str:
        """
        Visualize comparison of multiple models.

        Args:
            results: Dictionary with evaluation results for each model
            output_dir: Directory to save the visualization

        Returns:
            Path to the saved visualization
        """

    @staticmethod
    def generate_evaluation_report(
        results: Dict[str, Dict[str, Any]],
        output_path: str,
        include_visualizations: bool = True
    ) -> str:
        """
        Generate a comprehensive evaluation report.

        Args:
            results: Dictionary with evaluation results for each model
            output_path: Path to save the report
            include_visualizations: Whether to include visualizations in the report

        Returns:
            Path to the saved report
        """
```

### Functions

#### `evaluate_model`

Evaluate a fine-tuned model.

```python
def evaluate_model(
    model_path: str,
    dataset_path: str,
    metrics: List[Union[str, EvaluationMetric]] = None,
    output_dir: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Evaluate a fine-tuned model.

    Args:
        model_path: Path to the model
        dataset_path: Path to the dataset
        metrics: List of metrics to use for evaluation
        output_dir: Directory to save the results
        **kwargs: Additional parameters for evaluation

    Returns:
        Dictionary with evaluation results
    """
```

#### `compare_models`

Compare multiple fine-tuned models.

```python
def compare_models(
    model_paths: List[str],
    dataset_path: str,
    metrics: List[Union[str, EvaluationMetric]] = None,
    output_dir: Optional[str] = None,
    **kwargs
) -> Dict[str, Dict[str, Any]]:
    """
    Compare multiple fine-tuned models.

    Args:
        model_paths: List of paths to the models
        dataset_path: Path to the dataset
        metrics: List of metrics to use for evaluation
        output_dir: Directory to save the results
        **kwargs: Additional parameters for evaluation

    Returns:
        Dictionary with evaluation results for each model
    """
```

#### `generate_evaluation_report`

Generate a comprehensive evaluation report.

```python
def generate_evaluation_report(
    results: Dict[str, Dict[str, Any]],
    output_path: str,
    include_visualizations: bool = True
) -> str:
    """
    Generate a comprehensive evaluation report.

    Args:
        results: Dictionary with evaluation results for each model
        output_path: Path to save the report
        include_visualizations: Whether to include visualizations in the report

    Returns:
        Path to the saved report
    """
```

## Workflows

### Classes

#### `WorkflowStep`

Enum for workflow steps.

```python
class WorkflowStep(Enum):
    DATA_COLLECTION = "data_collection"
    FINE_TUNING = "fine_tuning"
    EVALUATION = "evaluation"
    COMPARISON = "comparison"
```

#### `WorkflowConfig`

Configuration for fine-tuning workflow.

```python
@dataclass
class WorkflowConfig:
    # Workflow name and output directory
    name: str
    output_dir: str

    # Steps to include in the workflow
    steps: List[WorkflowStep] = field(default_factory=lambda: [
        WorkflowStep.DATA_COLLECTION,
        WorkflowStep.FINE_TUNING,
        WorkflowStep.EVALUATION
    ])

    # Data collection configuration
    data_collection_config: Optional[DataCollectionConfig] = None

    # Fine-tuning configuration
    fine_tuning_config: Optional[FineTuningConfig] = None

    # Evaluation configuration
    evaluation_config: Optional[EvaluationConfig] = None

    # Comparison configuration
    comparison_models: List[str] = field(default_factory=list)

    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
```

#### `FineTuningWorkflow`

Class for running fine-tuning workflows.

```python
class FineTuningWorkflow:
    def __init__(self, config: WorkflowConfig):
        """
        Initialize the workflow.

        Args:
            config: Configuration for the workflow
        """

    def run(self) -> Dict[str, Any]:
        """
        Run the workflow.

        Returns:
            Dictionary with workflow results
        """
```

### Functions

#### `create_workflow`

Create a fine-tuning workflow.

```python
def create_workflow(config: WorkflowConfig) -> FineTuningWorkflow:
    """
    Create a fine-tuning workflow.

    Args:
        config: Configuration for the workflow

    Returns:
        Fine-tuning workflow
    """
```

#### `run_workflow`

Run a fine-tuning workflow.

```python
def run_workflow(config: WorkflowConfig) -> Dict[str, Any]:
    """
    Run a fine-tuning workflow.

    Args:
        config: Configuration for the workflow

    Returns:
        Dictionary with workflow results
    """
```

#### `save_workflow`

Save a workflow configuration to disk.

```python
def save_workflow(workflow: FineTuningWorkflow, path: str) -> str:
    """
    Save a workflow configuration to disk.

    Args:
        workflow: Workflow to save
        path: Path to save the workflow

    Returns:
        Path to the saved workflow
    """
```

#### `load_workflow`

Load a workflow configuration from disk.

```python
def load_workflow(path: str) -> FineTuningWorkflow:
    """
    Load a workflow configuration from disk.

    Args:
        path: Path to the workflow configuration

    Returns:
        Fine-tuning workflow
    """
```
