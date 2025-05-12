# Fine-Tuning Module

This module provides tools for fine-tuning AI models, including data collection, fine-tuning workflows, evaluation, and model comparison.

## Overview

The fine-tuning module consists of the following components:

- **Data Collection**: Tools for collecting, preparing, and exporting datasets for fine-tuning
- **Fine-Tuning**: Tools for fine-tuning AI models using various methods (LoRA, QLoRA, etc.)
- **Evaluation**: Tools for evaluating fine-tuned models using various metrics
- **Workflows**: Tools for creating and running end-to-end fine-tuning workflows

## Getting Started

### Installation

The fine-tuning module is part of the pAIssive_income project. To use it, you need to have the project installed.

```bash
# Clone the repository
git clone https://github.com/your-username/pAIssive_income.git
cd pAIssive_income

# Install dependencies
uv pip install -r requirements.txt
```

### Basic Usage

Here's a simple example of how to use the fine-tuning module:

```python
from ai_models.fine_tuning import (
    DataCollectionConfig, DataCollector,
    FineTuningConfig, FineTuningMethod, fine_tune_model,
    EvaluationConfig, evaluate_model
)

# Step 1: Prepare dataset
data_config = DataCollectionConfig(
    sources=["path/to/your/data.jsonl"],
    validation_split=0.1,
    test_split=0.1
)
collector = DataCollector(data_config)
dataset = collector.prepare()

# Step 2: Fine-tune model
fine_tuning_config = FineTuningConfig(
    model_path="your/base/model",
    output_dir="fine_tuned_model",
    method=FineTuningMethod.LORA,
    dataset=dataset
)
model_path = fine_tune_model(fine_tuning_config)

# Step 3: Evaluate model
results = evaluate_model(
    model_path=model_path,
    dataset=dataset,
    metrics=["perplexity", "accuracy"],
    output_dir="evaluation_results"
)
```

## Documentation

For more detailed information, refer to the documentation in the `docs` directory:

- [Fine-Tuning Best Practices](docs/fine_tuning_best_practices.md): Comprehensive guide to best practices for fine-tuning AI models
- [API Reference](docs/api_reference.md): Detailed API documentation for the fine-tuning module
- [Examples](docs/examples.md): Examples of how to use the fine-tuning module

## Examples

The `examples` directory contains example scripts that demonstrate how to use the fine-tuning module:

- `model_evaluation_example.py`: Example of how to evaluate and compare fine-tuned models

## License

This module is part of the pAIssive_income project and is licensed under the same license as the project.
