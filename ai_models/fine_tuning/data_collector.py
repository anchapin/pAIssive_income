"""
"""
Data collection tools for fine-tuning AI models.
Data collection tools for fine-tuning AI models.


This module provides tools for collecting, preparing, and exporting datasets
This module provides tools for collecting, preparing, and exporting datasets
for fine-tuning AI models.
for fine-tuning AI models.
"""
"""




import json
import json
import logging
import logging
import os
import os
from dataclasses import dataclass, field
from dataclasses import dataclass, field
from enum import Enum
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Union
from typing import Any, Callable, Dict, List, Optional, Union


from datasets import Dataset, DatasetDict, concatenate_datasets, load_dataset
from datasets import Dataset, DatasetDict, concatenate_datasets, load_dataset


# Configure logger
# Configure logger
logger = logging.getLogger(__name__)
logger = logging.getLogger(__name__)




class DatasetFormat(Enum):
    class DatasetFormat(Enum):
    """
    """
    Enum for dataset formats.
    Enum for dataset formats.
    """
    """


    JSONL = "jsonl"
    JSONL = "jsonl"
    CSV = "csv"
    CSV = "csv"
    PARQUET = "parquet"
    PARQUET = "parquet"
    HUGGINGFACE = "huggingface"
    HUGGINGFACE = "huggingface"
    CUSTOM = "custom"
    CUSTOM = "custom"




    @dataclass
    @dataclass
    class DataCollectionConfig:
    class DataCollectionConfig:
    """
    """
    Configuration for data collection.
    Configuration for data collection.
    """
    """


    # Dataset sources
    # Dataset sources
    sources: List[str] = field(default_factory=list)
    sources: List[str] = field(default_factory=list)


    # Output format
    # Output format
    output_format: DatasetFormat = DatasetFormat.JSONL
    output_format: DatasetFormat = DatasetFormat.JSONL


    # Output path
    # Output path
    output_path: Optional[str] = None
    output_path: Optional[str] = None


    # Data processing options
    # Data processing options
    shuffle: bool = True
    shuffle: bool = True
    max_samples: Optional[int] = None
    max_samples: Optional[int] = None


    # Filtering options
    # Filtering options
    min_length: Optional[int] = None
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    max_length: Optional[int] = None
    filter_function: Optional[Callable[[Dict[str, Any]], bool]] = None
    filter_function: Optional[Callable[[Dict[str, Any]], bool]] = None


    # Transformation options
    # Transformation options
    transform_function: Optional[Callable[[Dict[str, Any]], Dict[str, Any]]] = None
    transform_function: Optional[Callable[[Dict[str, Any]], Dict[str, Any]]] = None


    # Validation options
    # Validation options
    validation_split: float = 0.1
    validation_split: float = 0.1
    test_split: float = 0.1
    test_split: float = 0.1


    # Metadata
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)




    class DataCollector:
    class DataCollector:
    """
    """
    Class for collecting and preparing datasets for fine-tuning.
    Class for collecting and preparing datasets for fine-tuning.
    """
    """


    def __init__(self, config: DataCollectionConfig):
    def __init__(self, config: DataCollectionConfig):
    """
    """
    Initialize the data collector.
    Initialize the data collector.


    Args:
    Args:
    config: Configuration for data collection
    config: Configuration for data collection
    """
    """
    self.config = config
    self.config = config


    def collect(self) -> Dataset:
    def collect(self) -> Dataset:
    """
    """
    Collect data from the specified sources.
    Collect data from the specified sources.


    Returns:
    Returns:
    Collected dataset
    Collected dataset
    """
    """
    datasets = []
    datasets = []


    for source in self.config.sources:
    for source in self.config.sources:
    try:
    try:
    # Check if source is a file path or a Hugging Face dataset
    # Check if source is a file path or a Hugging Face dataset
    if os.path.exists(source):
    if os.path.exists(source):
    # Load from file
    # Load from file
    dataset = self._load_from_file(source)
    dataset = self._load_from_file(source)
    else:
    else:
    # Load from Hugging Face
    # Load from Hugging Face
    dataset = load_dataset(source)
    dataset = load_dataset(source)


    # If it's a DatasetDict, use the 'train' split
    # If it's a DatasetDict, use the 'train' split
    if isinstance(dataset, DatasetDict) and "train" in dataset:
    if isinstance(dataset, DatasetDict) and "train" in dataset:
    dataset = dataset["train"]
    dataset = dataset["train"]


    # Apply filtering
    # Apply filtering
    dataset = self._filter_dataset(dataset)
    dataset = self._filter_dataset(dataset)


    # Apply transformation
    # Apply transformation
    dataset = self._transform_dataset(dataset)
    dataset = self._transform_dataset(dataset)


    datasets.append(dataset)
    datasets.append(dataset)
    logger.info(f"Loaded dataset from {source} with {len(dataset)} samples")
    logger.info(f"Loaded dataset from {source} with {len(dataset)} samples")


except Exception as e:
except Exception as e:
    logger.error(f"Error loading dataset from {source}: {e}")
    logger.error(f"Error loading dataset from {source}: {e}")


    if not datasets:
    if not datasets:
    raise ValueError("No datasets were successfully loaded")
    raise ValueError("No datasets were successfully loaded")


    # Combine datasets
    # Combine datasets
    combined_dataset = concatenate_datasets(datasets)
    combined_dataset = concatenate_datasets(datasets)


    # Shuffle if requested
    # Shuffle if requested
    if self.config.shuffle:
    if self.config.shuffle:
    combined_dataset = combined_dataset.shuffle(seed=42)
    combined_dataset = combined_dataset.shuffle(seed=42)


    # Limit number of samples if requested
    # Limit number of samples if requested
    if self.config.max_samples and len(combined_dataset) > self.config.max_samples:
    if self.config.max_samples and len(combined_dataset) > self.config.max_samples:
    combined_dataset = combined_dataset.select(range(self.config.max_samples))
    combined_dataset = combined_dataset.select(range(self.config.max_samples))


    logger.info(f"Combined dataset has {len(combined_dataset)} samples")
    logger.info(f"Combined dataset has {len(combined_dataset)} samples")
    return combined_dataset
    return combined_dataset


    def prepare(self) -> DatasetDict:
    def prepare(self) -> DatasetDict:
    """
    """
    Prepare the dataset for fine-tuning, including train/validation/test splits.
    Prepare the dataset for fine-tuning, including train/validation/test splits.


    Returns:
    Returns:
    Prepared dataset with train, validation, and test splits
    Prepared dataset with train, validation, and test splits
    """
    """
    # Collect data
    # Collect data
    dataset = self.collect()
    dataset = self.collect()


    # Create train/validation/test splits
    # Create train/validation/test splits
    train_test_split = dataset.train_test_split(
    train_test_split = dataset.train_test_split(
    test_size=self.config.validation_split + self.config.test_split, seed=42
    test_size=self.config.validation_split + self.config.test_split, seed=42
    )
    )


    train_dataset = train_test_split["train"]
    train_dataset = train_test_split["train"]


    # Split the test set into validation and test
    # Split the test set into validation and test
    if self.config.test_split > 0:
    if self.config.test_split > 0:
    test_valid_ratio = self.config.test_split / (
    test_valid_ratio = self.config.test_split / (
    self.config.validation_split + self.config.test_split
    self.config.validation_split + self.config.test_split
    )
    )
    valid_test_split = train_test_split["test"].train_test_split(
    valid_test_split = train_test_split["test"].train_test_split(
    test_size=test_valid_ratio, seed=42
    test_size=test_valid_ratio, seed=42
    )
    )
    valid_dataset = valid_test_split["train"]
    valid_dataset = valid_test_split["train"]
    test_dataset = valid_test_split["test"]
    test_dataset = valid_test_split["test"]
    else:
    else:
    valid_dataset = train_test_split["test"]
    valid_dataset = train_test_split["test"]
    test_dataset = Dataset.from_dict({})
    test_dataset = Dataset.from_dict({})


    logger.info(
    logger.info(
    f"Dataset split: {len(train_dataset)} train, {len(valid_dataset)} validation, {len(test_dataset)} test"
    f"Dataset split: {len(train_dataset)} train, {len(valid_dataset)} validation, {len(test_dataset)} test"
    )
    )


    return DatasetDict(
    return DatasetDict(
    {"train": train_dataset, "validation": valid_dataset, "test": test_dataset}
    {"train": train_dataset, "validation": valid_dataset, "test": test_dataset}
    )
    )


    def export(self, dataset: Union[Dataset, DatasetDict]) -> str:
    def export(self, dataset: Union[Dataset, DatasetDict]) -> str:
    """
    """
    Export the dataset to the specified format.
    Export the dataset to the specified format.


    Args:
    Args:
    dataset: Dataset to export
    dataset: Dataset to export


    Returns:
    Returns:
    Path to the exported dataset
    Path to the exported dataset
    """
    """
    output_path = self.config.output_path
    output_path = self.config.output_path
    if not output_path:
    if not output_path:
    output_path = "dataset"
    output_path = "dataset"


    # Create output directory if it doesn't exist
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)


    # Export based on format
    # Export based on format
    if self.config.output_format == DatasetFormat.JSONL:
    if self.config.output_format == DatasetFormat.JSONL:
    return self._export_jsonl(dataset, output_path)
    return self._export_jsonl(dataset, output_path)
    elif self.config.output_format == DatasetFormat.CSV:
    elif self.config.output_format == DatasetFormat.CSV:
    return self._export_csv(dataset, output_path)
    return self._export_csv(dataset, output_path)
    elif self.config.output_format == DatasetFormat.PARQUET:
    elif self.config.output_format == DatasetFormat.PARQUET:
    return self._export_parquet(dataset, output_path)
    return self._export_parquet(dataset, output_path)
    elif self.config.output_format == DatasetFormat.HUGGINGFACE:
    elif self.config.output_format == DatasetFormat.HUGGINGFACE:
    return self._export_huggingface(dataset, output_path)
    return self._export_huggingface(dataset, output_path)
    else:
    else:
    raise ValueError(f"Unsupported output format: {self.config.output_format}")
    raise ValueError(f"Unsupported output format: {self.config.output_format}")


    def _load_from_file(self, file_path: str) -> Dataset:
    def _load_from_file(self, file_path: str) -> Dataset:
    """
    """
    Load a dataset from a file.
    Load a dataset from a file.


    Args:
    Args:
    file_path: Path to the file
    file_path: Path to the file


    Returns:
    Returns:
    Loaded dataset
    Loaded dataset
    """
    """
    # Determine file format from extension
    # Determine file format from extension
    _, ext = os.path.splitext(file_path)
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()
    ext = ext.lower()


    if ext == ".jsonl" or ext == ".json":
    if ext == ".jsonl" or ext == ".json":
    # Load JSONL file
    # Load JSONL file
    return Dataset.from_json(file_path)
    return Dataset.from_json(file_path)
    elif ext == ".csv":
    elif ext == ".csv":
    # Load CSV file
    # Load CSV file
    return Dataset.from_csv(file_path)
    return Dataset.from_csv(file_path)
    elif ext == ".parquet":
    elif ext == ".parquet":
    # Load Parquet file
    # Load Parquet file
    return Dataset.from_parquet(file_path)
    return Dataset.from_parquet(file_path)
    else:
    else:
    raise ValueError(f"Unsupported file format: {ext}")
    raise ValueError(f"Unsupported file format: {ext}")


    def _filter_dataset(self, dataset: Dataset) -> Dataset:
    def _filter_dataset(self, dataset: Dataset) -> Dataset:
    """
    """
    Filter the dataset based on the configuration.
    Filter the dataset based on the configuration.


    Args:
    Args:
    dataset: Dataset to filter
    dataset: Dataset to filter


    Returns:
    Returns:
    Filtered dataset
    Filtered dataset
    """
    """
    # Apply length filtering if specified
    # Apply length filtering if specified
    if self.config.min_length is not None or self.config.max_length is not None:
    if self.config.min_length is not None or self.config.max_length is not None:


    def length_filter(example):
    def length_filter(example):
    # Find a text field to filter on
    # Find a text field to filter on
    text_field = None
    text_field = None
    for field in ["text", "content", "input", "prompt", "question"]:
    for field in ["text", "content", "input", "prompt", "question"]:
    if field in example and isinstance(example[field], str):
    if field in example and isinstance(example[field], str):
    text_field = field
    text_field = field
    break
    break


    if text_field is None:
    if text_field is None:
    return True  # No text field found, keep the example
    return True  # No text field found, keep the example


    text_length = len(example[text_field])
    text_length = len(example[text_field])


    if (
    if (
    self.config.min_length is not None
    self.config.min_length is not None
    and text_length < self.config.min_length
    and text_length < self.config.min_length
    ):
    ):
    return False
    return False


    if (
    if (
    self.config.max_length is not None
    self.config.max_length is not None
    and text_length > self.config.max_length
    and text_length > self.config.max_length
    ):
    ):
    return False
    return False


    return True
    return True


    dataset = dataset.filter(length_filter)
    dataset = dataset.filter(length_filter)


    # Apply custom filter function if specified
    # Apply custom filter function if specified
    if self.config.filter_function is not None:
    if self.config.filter_function is not None:
    dataset = dataset.filter(self.config.filter_function)
    dataset = dataset.filter(self.config.filter_function)


    return dataset
    return dataset


    def _transform_dataset(self, dataset: Dataset) -> Dataset:
    def _transform_dataset(self, dataset: Dataset) -> Dataset:
    """
    """
    Transform the dataset based on the configuration.
    Transform the dataset based on the configuration.


    Args:
    Args:
    dataset: Dataset to transform
    dataset: Dataset to transform


    Returns:
    Returns:
    Transformed dataset
    Transformed dataset
    """
    """
    if self.config.transform_function is not None:
    if self.config.transform_function is not None:
    dataset = dataset.map(self.config.transform_function)
    dataset = dataset.map(self.config.transform_function)


    return dataset
    return dataset


    def _export_jsonl(
    def _export_jsonl(
    self, dataset: Union[Dataset, DatasetDict], output_path: str
    self, dataset: Union[Dataset, DatasetDict], output_path: str
    ) -> str:
    ) -> str:
    """
    """
    Export the dataset to JSONL format.
    Export the dataset to JSONL format.


    Args:
    Args:
    dataset: Dataset to export
    dataset: Dataset to export
    output_path: Base path for the output
    output_path: Base path for the output


    Returns:
    Returns:
    Path to the exported dataset
    Path to the exported dataset
    """
    """
    if isinstance(dataset, DatasetDict):
    if isinstance(dataset, DatasetDict):
    # Export each split
    # Export each split
    paths = {}
    paths = {}
    for split, split_dataset in dataset.items():
    for split, split_dataset in dataset.items():
    split_path = f"{output_path}_{split}.jsonl"
    split_path = f"{output_path}_{split}.jsonl"
    split_dataset.to_json(split_path)
    split_dataset.to_json(split_path)
    paths[split] = split_path
    paths[split] = split_path


    # Create a metadata file
    # Create a metadata file
    metadata_path = f"{output_path}_metadata.json"
    metadata_path = f"{output_path}_metadata.json"
    with open(metadata_path, "w", encoding="utf-8") as f:
    with open(metadata_path, "w", encoding="utf-8") as f:
    json.dump(
    json.dump(
    {
    {
    "format": "jsonl",
    "format": "jsonl",
    "splits": paths,
    "splits": paths,
    "metadata": self.config.metadata,
    "metadata": self.config.metadata,
    },
    },
    f,
    f,
    indent=2,
    indent=2,
    )
    )


    return metadata_path
    return metadata_path
    else:
    else:
    # Export single dataset
    # Export single dataset
    output_path = f"{output_path}.jsonl"
    output_path = f"{output_path}.jsonl"
    dataset.to_json(output_path)
    dataset.to_json(output_path)
    return output_path
    return output_path


    def _export_csv(
    def _export_csv(
    self, dataset: Union[Dataset, DatasetDict], output_path: str
    self, dataset: Union[Dataset, DatasetDict], output_path: str
    ) -> str:
    ) -> str:
    """
    """
    Export the dataset to CSV format.
    Export the dataset to CSV format.


    Args:
    Args:
    dataset: Dataset to export
    dataset: Dataset to export
    output_path: Base path for the output
    output_path: Base path for the output


    Returns:
    Returns:
    Path to the exported dataset
    Path to the exported dataset
    """
    """
    if isinstance(dataset, DatasetDict):
    if isinstance(dataset, DatasetDict):
    # Export each split
    # Export each split
    paths = {}
    paths = {}
    for split, split_dataset in dataset.items():
    for split, split_dataset in dataset.items():
    split_path = f"{output_path}_{split}.csv"
    split_path = f"{output_path}_{split}.csv"
    split_dataset.to_csv(split_path, index=False)
    split_dataset.to_csv(split_path, index=False)
    paths[split] = split_path
    paths[split] = split_path


    # Create a metadata file
    # Create a metadata file
    metadata_path = f"{output_path}_metadata.json"
    metadata_path = f"{output_path}_metadata.json"
    with open(metadata_path, "w", encoding="utf-8") as f:
    with open(metadata_path, "w", encoding="utf-8") as f:
    json.dump(
    json.dump(
    {
    {
    "format": "csv",
    "format": "csv",
    "splits": paths,
    "splits": paths,
    "metadata": self.config.metadata,
    "metadata": self.config.metadata,
    },
    },
    f,
    f,
    indent=2,
    indent=2,
    )
    )


    return metadata_path
    return metadata_path
    else:
    else:
    # Export single dataset
    # Export single dataset
    output_path = f"{output_path}.csv"
    output_path = f"{output_path}.csv"
    dataset.to_csv(output_path, index=False)
    dataset.to_csv(output_path, index=False)
    return output_path
    return output_path


    def _export_parquet(
    def _export_parquet(
    self, dataset: Union[Dataset, DatasetDict], output_path: str
    self, dataset: Union[Dataset, DatasetDict], output_path: str
    ) -> str:
    ) -> str:
    """
    """
    Export the dataset to Parquet format.
    Export the dataset to Parquet format.


    Args:
    Args:
    dataset: Dataset to export
    dataset: Dataset to export
    output_path: Base path for the output
    output_path: Base path for the output


    Returns:
    Returns:
    Path to the exported dataset
    Path to the exported dataset
    """
    """
    if isinstance(dataset, DatasetDict):
    if isinstance(dataset, DatasetDict):
    # Export each split
    # Export each split
    paths = {}
    paths = {}
    for split, split_dataset in dataset.items():
    for split, split_dataset in dataset.items():
    split_path = f"{output_path}_{split}.parquet"
    split_path = f"{output_path}_{split}.parquet"
    split_dataset.to_parquet(split_path)
    split_dataset.to_parquet(split_path)
    paths[split] = split_path
    paths[split] = split_path


    # Create a metadata file
    # Create a metadata file
    metadata_path = f"{output_path}_metadata.json"
    metadata_path = f"{output_path}_metadata.json"
    with open(metadata_path, "w", encoding="utf-8") as f:
    with open(metadata_path, "w", encoding="utf-8") as f:
    json.dump(
    json.dump(
    {
    {
    "format": "parquet",
    "format": "parquet",
    "splits": paths,
    "splits": paths,
    "metadata": self.config.metadata,
    "metadata": self.config.metadata,
    },
    },
    f,
    f,
    indent=2,
    indent=2,
    )
    )


    return metadata_path
    return metadata_path
    else:
    else:
    # Export single dataset
    # Export single dataset
    output_path = f"{output_path}.parquet"
    output_path = f"{output_path}.parquet"
    dataset.to_parquet(output_path)
    dataset.to_parquet(output_path)
    return output_path
    return output_path


    def _export_huggingface(
    def _export_huggingface(
    self, dataset: Union[Dataset, DatasetDict], output_path: str
    self, dataset: Union[Dataset, DatasetDict], output_path: str
    ) -> str:
    ) -> str:
    """
    """
    Export the dataset to Hugging Face format.
    Export the dataset to Hugging Face format.


    Args:
    Args:
    dataset: Dataset to export
    dataset: Dataset to export
    output_path: Base path for the output
    output_path: Base path for the output


    Returns:
    Returns:
    Path to the exported dataset
    Path to the exported dataset
    """
    """
    # Save the dataset to disk
    # Save the dataset to disk
    dataset.save_to_disk(output_path)
    dataset.save_to_disk(output_path)
    return output_path
    return output_path




    def collect_data(config: DataCollectionConfig) -> Dataset:
    def collect_data(config: DataCollectionConfig) -> Dataset:
    """
    """
    Collect data for fine-tuning.
    Collect data for fine-tuning.


    Args:
    Args:
    config: Configuration for data collection
    config: Configuration for data collection


    Returns:
    Returns:
    Collected dataset
    Collected dataset
    """
    """
    collector = DataCollector(config)
    collector = DataCollector(config)
    return collector.collect()
    return collector.collect()




    def prepare_dataset(config: DataCollectionConfig) -> DatasetDict:
    def prepare_dataset(config: DataCollectionConfig) -> DatasetDict:
    """
    """
    Prepare a dataset for fine-tuning.
    Prepare a dataset for fine-tuning.


    Args:
    Args:
    config: Configuration for data collection
    config: Configuration for data collection


    Returns:
    Returns:
    Prepared dataset with train, validation, and test splits
    Prepared dataset with train, validation, and test splits
    """
    """
    collector = DataCollector(config)
    collector = DataCollector(config)
    return collector.prepare()
    return collector.prepare()




    def export_dataset(
    def export_dataset(
    dataset: Union[Dataset, DatasetDict],
    dataset: Union[Dataset, DatasetDict],
    output_path: str,
    output_path: str,
    format: Union[str, DatasetFormat] = DatasetFormat.JSONL,
    format: Union[str, DatasetFormat] = DatasetFormat.JSONL,
    metadata: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
    ) -> str:
    """
    """
    Export a dataset to the specified format.
    Export a dataset to the specified format.


    Args:
    Args:
    dataset: Dataset to export
    dataset: Dataset to export
    output_path: Path for the output
    output_path: Path for the output
    format: Output format
    format: Output format
    metadata: Metadata to include
    metadata: Metadata to include


    Returns:
    Returns:
    Path to the exported dataset
    Path to the exported dataset
    """
    """
    # Convert format to enum if it's a string
    # Convert format to enum if it's a string
    if isinstance(format, str):
    if isinstance(format, str):
    try:
    try:
    format = DatasetFormat(format)
    format = DatasetFormat(format)
except ValueError:
except ValueError:
    format = DatasetFormat.JSONL
    format = DatasetFormat.JSONL


    # Create configuration
    # Create configuration
    config = DataCollectionConfig(
    config = DataCollectionConfig(
    output_format=format, output_path=output_path, metadata=metadata or {}
    output_format=format, output_path=output_path, metadata=metadata or {}
    )
    )


    # Export dataset
    # Export dataset
    collector = DataCollector(config)
    collector = DataCollector(config)
    return collector.export(dataset)
    return collector.export(dataset)