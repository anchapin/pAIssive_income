# Fine-Tuning Examples

This document provides examples of how to use the fine-tuning module in the pAIssive_income project.

## Table of Contents

- [Data Collection](#data-collection)
- [Fine-Tuning](#fine-tuning)
- [Evaluation](#evaluation)
- [Model Comparison](#model-comparison)
- [End-to-End Workflow](#end-to-end-workflow)

## Data Collection

### Basic Data Collection

```python
from ai_models.fine_tuning import DataCollectionConfig, DataCollector, DatasetFormat

# Create configuration
config = DataCollectionConfig(
    sources=["path/to/your/data.jsonl"],
    output_format=DatasetFormat.JSONL,
    output_path="prepared_dataset",
    shuffle=True,
    validation_split=0.1,
    test_split=0.1
)

# Create collector and prepare dataset
collector = DataCollector(config)
dataset = collector.prepare()

# Export the dataset
collector.export(dataset)
```

### Advanced Data Collection with Filtering and Transformation

```python
from ai_models.fine_tuning import DataCollectionConfig, DataCollector, DatasetFormat

# Define a filter function
def filter_function(example):
    # Filter out examples with short text
    if len(example["text"]) < 100:
        return False
    # Filter out examples with specific keywords
    if "unwanted_keyword" in example["text"].lower():
        return False
    return True

# Define a transformation function
def transform_function(example):
    # Add a new field
    example["text_length"] = len(example["text"])
    # Modify existing field
    example["text"] = example["text"].strip()
    return example

# Create configuration
config = DataCollectionConfig(
    sources=["path/to/your/data.jsonl", "path/to/another/data.csv"],
    output_format=DatasetFormat.JSONL,
    output_path="prepared_dataset",
    shuffle=True,
    validation_split=0.1,
    test_split=0.1,
    filter_function=filter_function,
    transform_function=transform_function,
    min_length=100,
    max_length=5000,
    max_samples=10000
)

# Create collector and prepare dataset
collector = DataCollector(config)
dataset = collector.prepare()

# Export the dataset
collector.export(dataset)
```

### Combining Multiple Datasets

```python
from ai_models.fine_tuning import DataCollectionConfig, DataCollector, DatasetFormat
from datasets import concatenate_datasets, Dataset

# Prepare first dataset
config1 = DataCollectionConfig(
    sources=["path/to/first/data.jsonl"],
    output_format=DatasetFormat.JSONL,
    output_path="first_dataset"
)
collector1 = DataCollector(config1)
dataset1 = collector1.prepare()

# Prepare second dataset
config2 = DataCollectionConfig(
    sources=["path/to/second/data.jsonl"],
    output_format=DatasetFormat.JSONL,
    output_path="second_dataset"
)
collector2 = DataCollector(config2)
dataset2 = collector2.prepare()

# Combine datasets
combined_dataset = {}
for split in dataset1:
    combined_dataset[split] = concatenate_datasets([dataset1[split], dataset2[split]])

# Export combined dataset
collector1.export(combined_dataset, "combined_dataset")
```

## Fine-Tuning

### Basic Fine-Tuning with LoRA

```python
from ai_models.fine_tuning import FineTuningConfig, FineTuningMethod, fine_tune_model

# Create configuration
config = FineTuningConfig(
    model_path="your/base/model",
    output_dir="fine_tuned_model",
    method=FineTuningMethod.LORA,
    dataset_path="prepared_dataset",
    num_train_epochs=3,
    learning_rate=2e-5,
    lora_r=8,
    lora_alpha=16,
    lora_dropout=0.05
)

# Fine-tune model
model_path = fine_tune_model(config)
```

### Fine-Tuning with QLoRA for Memory Efficiency

```python
from ai_models.fine_tuning import FineTuningConfig, FineTuningMethod, fine_tune_model

# Create configuration
config = FineTuningConfig(
    model_path="your/base/model",
    output_dir="fine_tuned_model",
    method=FineTuningMethod.QLORA,
    dataset_path="prepared_dataset",
    num_train_epochs=3,
    learning_rate=1e-4,
    per_device_train_batch_size=1,
    gradient_accumulation_steps=4,
    lora_r=16,
    lora_alpha=32,
    quantization_bits=4
)

# Fine-tune model
model_path = fine_tune_model(config)
```

### Full Fine-Tuning for Maximum Performance

```python
from ai_models.fine_tuning import FineTuningConfig, FineTuningMethod, fine_tune_model

# Create configuration
config = FineTuningConfig(
    model_path="your/base/model",
    output_dir="fine_tuned_model",
    method=FineTuningMethod.FULL,
    dataset_path="prepared_dataset",
    num_train_epochs=3,
    learning_rate=5e-6,
    per_device_train_batch_size=2,
    gradient_accumulation_steps=8,
    weight_decay=0.01,
    warmup_steps=100,
    max_length=512,
    early_stopping_patience=3
)

# Fine-tune model
model_path = fine_tune_model(config)
```

### Resuming Fine-Tuning from a Checkpoint

```python
from ai_models.fine_tuning import resume_fine_tuning

# Resume fine-tuning
model_path = resume_fine_tuning(
    output_dir="fine_tuned_model",
    checkpoint_dir="fine_tuned_model/checkpoint-1000"
)
```

## Evaluation

### Basic Model Evaluation

```python
from ai_models.fine_tuning import EvaluationConfig, ModelEvaluator, EvaluationMetric

# Create configuration
config = EvaluationConfig(
    model_path="your/fine_tuned/model",
    dataset_path="test_dataset",
    metrics=[EvaluationMetric.PERPLEXITY, EvaluationMetric.ACCURACY],
    output_dir="evaluation_results"
)

# Create evaluator and evaluate
evaluator = ModelEvaluator(config)
results = evaluator.evaluate()

# Visualize results
evaluator.visualize_results()
```

### Custom Evaluation Function

```python
from ai_models.fine_tuning import EvaluationConfig, ModelEvaluator, EvaluationMetric

# Define custom evaluation function
def custom_evaluation(model, tokenizer, dataset, device):
    # Implement custom evaluation logic
    results = {}
    
    # Example: Calculate average response length
    total_length = 0
    
    for i in range(min(10, len(dataset))):
        input_text = dataset[i]["input"]
        inputs = tokenizer(input_text, return_tensors="pt").to(device)
        
        with torch.no_grad():
            outputs = model.generate(
                inputs["input_ids"],
                max_length=100,
                num_return_sequences=1
            )
        
        output_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        total_length += len(output_text)
    
    results["avg_response_length"] = total_length / min(10, len(dataset))
    
    return results

# Create configuration
config = EvaluationConfig(
    model_path="your/fine_tuned/model",
    dataset_path="test_dataset",
    metrics=[EvaluationMetric.PERPLEXITY, EvaluationMetric.CUSTOM],
    custom_evaluation_function=custom_evaluation,
    output_dir="evaluation_results"
)

# Create evaluator and evaluate
evaluator = ModelEvaluator(config)
results = evaluator.evaluate()
```

### Using the Helper Function

```python
from ai_models.fine_tuning import evaluate_model

# Evaluate model
results = evaluate_model(
    model_path="your/fine_tuned/model",
    dataset_path="test_dataset",
    metrics=["perplexity", "accuracy"],
    output_dir="evaluation_results",
    num_samples=100,
    batch_size=4
)

print(results)
```

## Model Comparison

### Comparing Multiple Models

```python
from ai_models.fine_tuning import compare_models, generate_evaluation_report

# Compare models
results = compare_models(
    model_paths=[
        "base_model",
        "lora_fine_tuned_model",
        "qlora_fine_tuned_model",
        "full_fine_tuned_model"
    ],
    dataset_path="test_dataset",
    metrics=["perplexity", "accuracy", "rouge"],
    output_dir="comparison_results",
    num_samples=100
)

# Generate report
report_path = generate_evaluation_report(
    results,
    "comparison_report.md",
    include_visualizations=True
)
```

## End-to-End Workflow

### Complete Fine-Tuning Workflow

```python
from ai_models.fine_tuning import (
    WorkflowConfig, WorkflowStep,
    DataCollectionConfig, FineTuningConfig, EvaluationConfig,
    FineTuningMethod, EvaluationMetric,
    run_workflow
)

# Create data collection configuration
data_config = DataCollectionConfig(
    sources=["path/to/your/data.jsonl"],
    output_format="jsonl",
    validation_split=0.1,
    test_split=0.1
)

# Create fine-tuning configuration
fine_tuning_config = FineTuningConfig(
    model_path="your/base/model",
    output_dir="workflow_output/fine_tuned_model",
    method=FineTuningMethod.LORA,
    num_train_epochs=3,
    learning_rate=2e-5,
    lora_r=8,
    lora_alpha=16
)

# Create evaluation configuration
eval_config = EvaluationConfig(
    metrics=[EvaluationMetric.PERPLEXITY, EvaluationMetric.ACCURACY],
    output_dir="workflow_output/evaluation",
    num_samples=100
)

# Create workflow configuration
workflow_config = WorkflowConfig(
    name="Complete Fine-Tuning Workflow",
    output_dir="workflow_output",
    steps=[
        WorkflowStep.DATA_COLLECTION,
        WorkflowStep.FINE_TUNING,
        WorkflowStep.EVALUATION,
        WorkflowStep.COMPARISON
    ],
    data_collection_config=data_config,
    fine_tuning_config=fine_tuning_config,
    evaluation_config=eval_config,
    comparison_models=["another/model/to/compare"]
)

# Run workflow
results = run_workflow(workflow_config)

print(results)
```

### Saving and Loading Workflows

```python
from ai_models.fine_tuning import (
    WorkflowConfig, create_workflow,
    save_workflow, load_workflow
)

# Create workflow configuration
workflow_config = WorkflowConfig(
    name="My Workflow",
    output_dir="workflow_output"
    # ... other configuration ...
)

# Create workflow
workflow = create_workflow(workflow_config)

# Save workflow
save_path = save_workflow(workflow, "saved_workflow.json")

# Load workflow
loaded_workflow = load_workflow("saved_workflow.json")

# Run loaded workflow
results = loaded_workflow.run()
```

## Command-Line Example

You can also use the provided example script to evaluate and compare models from the command line:

```bash
# Evaluate a single model
python -m ai_models.examples.model_evaluation_example \
    --model "your/fine_tuned/model" \
    --dataset "test_dataset" \
    --output-dir "evaluation_results" \
    --metrics perplexity accuracy \
    --num-samples 100

# Compare multiple models
python -m ai_models.examples.model_evaluation_example \
    --models "model1" "model2" "model3" \
    --dataset "test_dataset" \
    --output-dir "comparison_results" \
    --metrics perplexity accuracy rouge \
    --num-samples 100
```
