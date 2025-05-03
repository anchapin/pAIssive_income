"""
Data collection tools for fine-tuning AI models.

This module provides tools for collecting, preparing, and exporting datasets
for fine-tuning AI models.
"""

import csv
import json
import logging
import os
import random
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

import pandas as pd
from datasets import Dataset, DatasetDict, concatenate_datasets, load_dataset

# Configure logger
logger = logging.getLogger(__name__)


class DatasetFormat(Enum):
    """
    Enum for dataset formats.
    """

    JSONL = "jsonl"
    CSV = "csv"
    PARQUET = "parquet"
    HUGGINGFACE = "huggingface"
    CUSTOM = "custom"


@dataclass
class DataCollectionConfig:
    """
    Configuration for data collection.
    """

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


class DataCollector:
    """
    Class for collecting and preparing datasets for fine-tuning.
    """

    def __init__(self, config: DataCollectionConfig):
        """
        Initialize the data collector.

        Args:
            config: Configuration for data collection
        """
        self.config = config

    def collect(self) -> Dataset:
        """
        Collect data from the specified sources.

        Returns:
            Collected dataset
        """
        datasets = []

        for source in self.config.sources:
            try:
                # Check if source is a file path or a Hugging Face dataset
                if os.path.exists(source):
                    # Load from file
                    dataset = self._load_from_file(source)
                else:
                    # Load from Hugging Face
                    dataset = load_dataset(source)

                    # If it's a DatasetDict, use the 'train' split
                    if isinstance(dataset, DatasetDict) and "train" in dataset:
                        dataset = dataset["train"]

                # Apply filtering
                dataset = self._filter_dataset(dataset)

                # Apply transformation
                dataset = self._transform_dataset(dataset)

                datasets.append(dataset)
                logger.info(f"Loaded dataset from {source} with {len(dataset)} samples")

            except Exception as e:
                logger.error(f"Error loading dataset from {source}: {e}")

        if not datasets:
            raise ValueError("No datasets were successfully loaded")

        # Combine datasets
        combined_dataset = concatenate_datasets(datasets)

        # Shuffle if requested
        if self.config.shuffle:
            combined_dataset = combined_dataset.shuffle(seed=42)

        # Limit number of samples if requested
        if self.config.max_samples and len(combined_dataset) > self.config.max_samples:
            combined_dataset = combined_dataset.select(range(self.config.max_samples))

        logger.info(f"Combined dataset has {len(combined_dataset)} samples")
        return combined_dataset

    def prepare(self) -> DatasetDict:
        """
        Prepare the dataset for fine-tuning, including train/validation/test splits.

        Returns:
            Prepared dataset with train, validation, and test splits
        """
        # Collect data
        dataset = self.collect()

        # Create train/validation/test splits
        train_test_split = dataset.train_test_split(
            test_size=self.config.validation_split + self.config.test_split, seed=42
        )

        train_dataset = train_test_split["train"]

        # Split the test set into validation and test
        if self.config.test_split > 0:
            test_valid_ratio = self.config.test_split / (
                self.config.validation_split + self.config.test_split
            )
            valid_test_split = train_test_split["test"].train_test_split(
                test_size=test_valid_ratio, seed=42
            )
            valid_dataset = valid_test_split["train"]
            test_dataset = valid_test_split["test"]
        else:
            valid_dataset = train_test_split["test"]
            test_dataset = Dataset.from_dict({})

        logger.info(
            f"Dataset split: {len(train_dataset)} train, {len(valid_dataset)} validation, {len(test_dataset)} test"
        )

        return DatasetDict(
            {"train": train_dataset, "validation": valid_dataset, "test": test_dataset}
        )

    def export(self, dataset: Union[Dataset, DatasetDict]) -> str:
        """
        Export the dataset to the specified format.

        Args:
            dataset: Dataset to export

        Returns:
            Path to the exported dataset
        """
        output_path = self.config.output_path
        if not output_path:
            output_path = "dataset"

        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Export based on format
        if self.config.output_format == DatasetFormat.JSONL:
            return self._export_jsonl(dataset, output_path)
        elif self.config.output_format == DatasetFormat.CSV:
            return self._export_csv(dataset, output_path)
        elif self.config.output_format == DatasetFormat.PARQUET:
            return self._export_parquet(dataset, output_path)
        elif self.config.output_format == DatasetFormat.HUGGINGFACE:
            return self._export_huggingface(dataset, output_path)
        else:
            raise ValueError(f"Unsupported output format: {self.config.output_format}")

    def _load_from_file(self, file_path: str) -> Dataset:
        """
        Load a dataset from a file.

        Args:
            file_path: Path to the file

        Returns:
            Loaded dataset
        """
        # Determine file format from extension
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()

        if ext == ".jsonl" or ext == ".json":
            # Load JSONL file
            return Dataset.from_json(file_path)
        elif ext == ".csv":
            # Load CSV file
            return Dataset.from_csv(file_path)
        elif ext == ".parquet":
            # Load Parquet file
            return Dataset.from_parquet(file_path)
        else:
            raise ValueError(f"Unsupported file format: {ext}")

    def _filter_dataset(self, dataset: Dataset) -> Dataset:
        """
        Filter the dataset based on the configuration.

        Args:
            dataset: Dataset to filter

        Returns:
            Filtered dataset
        """
        # Apply length filtering if specified
        if self.config.min_length is not None or self.config.max_length is not None:

            def length_filter(example):
                # Find a text field to filter on
                text_field = None
                for field in ["text", "content", "input", "prompt", "question"]:
                    if field in example and isinstance(example[field], str):
                        text_field = field
                        break

                if text_field is None:
                    return True  # No text field found, keep the example

                text_length = len(example[text_field])

                if self.config.min_length is not None and text_length < self.config.min_length:
                    return False

                if self.config.max_length is not None and text_length > self.config.max_length:
                    return False

                return True

            dataset = dataset.filter(length_filter)

        # Apply custom filter function if specified
        if self.config.filter_function is not None:
            dataset = dataset.filter(self.config.filter_function)

        return dataset

    def _transform_dataset(self, dataset: Dataset) -> Dataset:
        """
        Transform the dataset based on the configuration.

        Args:
            dataset: Dataset to transform

        Returns:
            Transformed dataset
        """
        if self.config.transform_function is not None:
            dataset = dataset.map(self.config.transform_function)

        return dataset

    def _export_jsonl(self, dataset: Union[Dataset, DatasetDict], output_path: str) -> str:
        """
        Export the dataset to JSONL format.

        Args:
            dataset: Dataset to export
            output_path: Base path for the output

        Returns:
            Path to the exported dataset
        """
        if isinstance(dataset, DatasetDict):
            # Export each split
            paths = {}
            for split, split_dataset in dataset.items():
                split_path = f"{output_path}_{split}.jsonl"
                split_dataset.to_json(split_path)
                paths[split] = split_path

            # Create a metadata file
            metadata_path = f"{output_path}_metadata.json"
            with open(metadata_path, "w", encoding="utf-8") as f:
                json.dump(
                    {"format": "jsonl", "splits": paths, "metadata": self.config.metadata},
                    f,
                    indent=2,
                )

            return metadata_path
        else:
            # Export single dataset
            output_path = f"{output_path}.jsonl"
            dataset.to_json(output_path)
            return output_path

    def _export_csv(self, dataset: Union[Dataset, DatasetDict], output_path: str) -> str:
        """
        Export the dataset to CSV format.

        Args:
            dataset: Dataset to export
            output_path: Base path for the output

        Returns:
            Path to the exported dataset
        """
        if isinstance(dataset, DatasetDict):
            # Export each split
            paths = {}
            for split, split_dataset in dataset.items():
                split_path = f"{output_path}_{split}.csv"
                split_dataset.to_csv(split_path, index=False)
                paths[split] = split_path

            # Create a metadata file
            metadata_path = f"{output_path}_metadata.json"
            with open(metadata_path, "w", encoding="utf-8") as f:
                json.dump(
                    {"format": "csv", "splits": paths, "metadata": self.config.metadata},
                    f,
                    indent=2,
                )

            return metadata_path
        else:
            # Export single dataset
            output_path = f"{output_path}.csv"
            dataset.to_csv(output_path, index=False)
            return output_path

    def _export_parquet(self, dataset: Union[Dataset, DatasetDict], output_path: str) -> str:
        """
        Export the dataset to Parquet format.

        Args:
            dataset: Dataset to export
            output_path: Base path for the output

        Returns:
            Path to the exported dataset
        """
        if isinstance(dataset, DatasetDict):
            # Export each split
            paths = {}
            for split, split_dataset in dataset.items():
                split_path = f"{output_path}_{split}.parquet"
                split_dataset.to_parquet(split_path)
                paths[split] = split_path

            # Create a metadata file
            metadata_path = f"{output_path}_metadata.json"
            with open(metadata_path, "w", encoding="utf-8") as f:
                json.dump(
                    {"format": "parquet", "splits": paths, "metadata": self.config.metadata},
                    f,
                    indent=2,
                )

            return metadata_path
        else:
            # Export single dataset
            output_path = f"{output_path}.parquet"
            dataset.to_parquet(output_path)
            return output_path

    def _export_huggingface(self, dataset: Union[Dataset, DatasetDict], output_path: str) -> str:
        """
        Export the dataset to Hugging Face format.

        Args:
            dataset: Dataset to export
            output_path: Base path for the output

        Returns:
            Path to the exported dataset
        """
        # Save the dataset to disk
        dataset.save_to_disk(output_path)
        return output_path


def collect_data(config: DataCollectionConfig) -> Dataset:
    """
    Collect data for fine-tuning.

    Args:
        config: Configuration for data collection

    Returns:
        Collected dataset
    """
    collector = DataCollector(config)
    return collector.collect()


def prepare_dataset(config: DataCollectionConfig) -> DatasetDict:
    """
    Prepare a dataset for fine-tuning.

    Args:
        config: Configuration for data collection

    Returns:
        Prepared dataset with train, validation, and test splits
    """
    collector = DataCollector(config)
    return collector.prepare()


def export_dataset(
    dataset: Union[Dataset, DatasetDict],
    output_path: str,
    format: Union[str, DatasetFormat] = DatasetFormat.JSONL,
    metadata: Optional[Dict[str, Any]] = None,
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
    # Convert format to enum if it's a string
    if isinstance(format, str):
        try:
            format = DatasetFormat(format)
        except ValueError:
            format = DatasetFormat.JSONL

    # Create configuration
    config = DataCollectionConfig(
        output_format=format, output_path=output_path, metadata=metadata or {}
    )

    # Export dataset
    collector = DataCollector(config)
    return collector.export(dataset)
