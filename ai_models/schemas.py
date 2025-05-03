"""
Pydantic schemas for the AI Models module.

This module provides Pydantic models for data validation in the AI models module.
"""

import os
from datetime import datetime
from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ModelConfigSchema(BaseModel):
    """
    Pydantic model for AI model configuration.
    """

    models_dir: str = Field(
        default_factory=lambda: os.path.join(os.path.expanduser("~"), ".pAIssive_income", 
            "models"),
        description="Directory for storing AI models",
        pattern=r"^[a - zA - Z0 - 9_\-./]+$",  # Secure path pattern
    )
    cache_dir: str = Field(
        default_factory=lambda: os.path.join(os.path.expanduser("~"), ".pAIssive_income", 
            "cache"),
        description="Directory for caching model outputs",
        pattern=r"^[a - zA - Z0 - 9_\-./]+$",  # Secure path pattern
    )
    cache_enabled: bool = Field(default=True, description="Whether to enable caching")
    cache_ttl: int = Field(
        default=86400,  # 24 hours in seconds
        description="Time - to - live for cache entries in seconds",
        ge=0,
    )
    max_cache_size: int = Field(
        default=1000, description="Maximum number of items in memory cache", gt=0
    )
    default_device: str = Field(
        default="auto",
        description="Default device for model inference (auto, cpu, cuda, mps, etc.)",
        pattern=r"^[a - zA - Z0 - 9_\-]+$",  # Secure device name pattern
    )
    max_threads: Optional[int] = Field(
        default=None,
        description="Maximum number of threads to use (None means use all available threads)",
            
    )
    auto_discover: bool = Field(
        default=True, description="Whether to automatically discover models"
    )
    model_sources: List[str] = Field(
        default_factory=lambda: ["local", "huggingface"],
        description="Sources for model discovery",
    )
    default_text_model: str = Field(
        default="gpt2",
        description="Default text generation model",
        pattern=r"^[a - zA - Z0 - 9_\-]+$",  # Secure model name pattern
    )
    default_embedding_model: str = Field(
        default="all - MiniLM - L6 - v2",
        description="Default text embedding model",
        pattern=r"^[a - zA - Z0 - 9_\-]+$",  # Secure model name pattern
    )

    model_config = ConfigDict(
        validate_assignment=True,
        extra="ignore",
        arbitrary_types_allowed=True,
        str_strip_whitespace=True,  # Security: strip whitespace from strings
        str_max_length=1024,  # Security: limit string lengths
    )

    @field_validator("max_threads")
    @classmethod
    def validate_max_threads(cls, v: Optional[int]) -> Optional[int]:
        """Validate max_threads"""
        if v is not None and v <= 0:
            raise ValueError("max_threads must be positive or None")
        return v

    @field_validator("model_sources")
    @classmethod
    def validate_model_sources(cls, v: List[str]) -> List[str]:
        """Validate model sources"""
        valid_sources = {"local", "huggingface", "ollama"}
        invalid_sources = set(v) - valid_sources
        if invalid_sources:
            raise ValueError(
                f"Invalid model sources: {invalid_sources}. Must be one of {valid_sources}"
            )
        return v


class ModelInfoSchema(BaseModel):
    """
    Pydantic model for AI model information.
    """

    id: str = Field(
        ...,
        description="Unique identifier for the model",
        pattern=r"^[a - zA - Z0 - 9_\-]+$",  # Secure ID pattern
    )
    name: str = Field(
        ..., description="Name of the model", 
            pattern=r"^[a - zA - Z0 - 9_\-\s]+$"  # Secure name pattern
    )
    model_type: str = Field(
        ...,
        description="Type of model (text, embedding, etc.)",
        pattern=r"^[a - zA - Z0 - 9_\-]+$",  # Secure type pattern
    )
    framework: str = Field(
        ...,
        description="Framework used by the model (pytorch, tensorflow, etc.)",
        pattern=r"^[a - zA - Z0 - 9_\-]+$",  # Secure framework pattern
    )
    path: str = Field(
        ...,
        description="Path to the model files",
        pattern=r"^[a - zA - Z0 - 9_\-./]+$",  # Secure path pattern
    )
    description: Optional[str] = Field(None, description="Description of the model")
    version: Optional[str] = Field(
        None,
        description="Version of the model",
        pattern=r"^[0 - 9]+\.[0 - 9]+\.[0 - 9]+$",  # Semver pattern
    )
    created_at: datetime = Field(default_factory=datetime.now, 
        description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, 
        description="Last update timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, 
        description="Additional metadata")

    model_config = ConfigDict(
        validate_assignment=True,
        extra="ignore",
        str_strip_whitespace=True,  # Security: strip whitespace from strings
        str_max_length=1024,  # Security: limit string lengths
        json_schema_extra={"json_encoders": {datetime: lambda v: v.isoformat()}},
    )


class ModelParametersSchema(BaseModel):
    """
    Pydantic model for AI model parameters.
    """

    temperature: Optional[float] = Field(
        default=0.7, description="Temperature for sampling", ge=0.0, le=2.0
    )
    max_tokens: Optional[int] = Field(
        default=100, description="Maximum number of tokens to generate", gt=0, le=2048
    )
    top_p: Optional[float] = Field(
        default=0.9, description="Top - p sampling parameter", ge=0.0, le=1.0
    )
    top_k: Optional[int] = Field(default=50, description="Top - k sampling parameter", 
        ge=0, le=100)
    repetition_penalty: Optional[float] = Field(
        default=1.0, description="Repetition penalty", ge=0.0, le=2.0
    )
    stop_sequences: Optional[List[str]] = Field(
        default_factory=list,
        description="Sequences that stop generation",
        max_length=10,  # Security: limit number of stop sequences
    )

    model_config = ConfigDict(
        validate_assignment=True,
        extra="allow",
        str_strip_whitespace=True,
        str_max_length=100,  # Security: limit stop sequence lengths
    )


class TextGenerationRequestSchema(BaseModel):
    """
    Pydantic model for text generation request.
    """

    prompt: str = Field(
        ...,
        description="Input prompt for text generation",
        min_length=1,
        max_length=4096,  # Security: limit prompt length
    )
    model_id: Optional[str] = Field(
        None,
        description="ID of the model to use",
        pattern=r"^[a - zA - Z0 - 9_\-]+$",  # Secure model ID pattern
    )
    parameters: Optional[ModelParametersSchema] = Field(
        default_factory=ModelParametersSchema, description="Generation parameters"
    )

    model_config = ConfigDict(validate_assignment=True, extra="ignore", 
        str_strip_whitespace=True)


class TextGenerationResponseSchema(BaseModel):
    """
    Pydantic model for text generation response.
    """

    text: str = Field(..., description="Generated text")
    model_id: str = Field(
        ...,
        description="ID of the model used",
        pattern=r"^[a - zA - Z0 - 9_\-]+$",  # Secure model ID pattern
    )
    prompt: str = Field(..., description="Input prompt")
    parameters: ModelParametersSchema = Field(..., 
        description="Generation parameters used")
    tokens_generated: int = Field(..., description="Number of tokens generated", ge=0)
    generation_time: float = Field(..., 
        description="Time taken for generation in seconds", ge=0)
    created_at: datetime = Field(default_factory=datetime.now, 
        description="Creation timestamp")

    model_config = ConfigDict(
        validate_assignment=True,
        extra="ignore",
        str_strip_whitespace=True,
        str_max_length=8192,  # Security: limit response length
        json_schema_extra={"json_encoders": {datetime: lambda v: v.isoformat()}},
    )


class EmbeddingRequestSchema(BaseModel):
    """
    Pydantic model for text embedding request.
    """

    text: Union[str, List[str]] = Field(
        ..., description="Text to embed", 
            max_length=4096  # Security: limit input length
    )
    model_id: Optional[str] = Field(
        None,
        description="ID of the model to use",
        pattern=r"^[a - zA - Z0 - 9_\-]+$",  # Secure model ID pattern
    )

    model_config = ConfigDict(validate_assignment=True, extra="ignore", 
        str_strip_whitespace=True)


class EmbeddingResponseSchema(BaseModel):
    """
    Pydantic model for text embedding response.
    """

    embeddings: List[List[float]] = Field(..., description="Text embeddings")
    model_id: str = Field(
        ...,
        description="ID of the model used",
        pattern=r"^[a - zA - Z0 - 9_\-]+$",  # Secure model ID pattern
    )
    dimensions: int = Field(..., description="Dimensions of the embeddings", gt=0)
    texts: List[str] = Field(..., description="Input texts")
    embedding_time: float = Field(..., description="Time taken for embedding in seconds", 
        ge=0)
    created_at: datetime = Field(default_factory=datetime.now, 
        description="Creation timestamp")

    model_config = ConfigDict(
        validate_assignment=True,
        extra="ignore",
        str_strip_whitespace=True,
        json_schema_extra={"json_encoders": {datetime: lambda v: v.isoformat()}},
    )


class BenchmarkConfigSchema(BaseModel):
    """
    Pydantic model for benchmark configuration.
    """

    name: str = Field(
        ...,
        description="Name of the benchmark",
        pattern=r"^[a - zA - Z0 - 9_\-\s]+$",  # Secure name pattern
    )
    description: Optional[str] = Field(None, description="Description of the benchmark")
    model_ids: List[str] = Field(
        ..., description="IDs of models to benchmark", 
            min_length=1  # Must have at least one model
    )
    metrics: List[str] = Field(
        ..., description="Metrics to evaluate", 
            min_length=1  # Must have at least one metric
    )
    input_file: Optional[str] = Field(
        None,
        description="Path to input file",
        pattern=r"^[a - zA - Z0 - 9_\-./]+$",  # Secure path pattern
    )
    output_dir: str = Field(
        ...,
        description="Directory for output files",
        pattern=r"^[a - zA - Z0 - 9_\-./]+$",  # Secure path pattern
    )
    num_samples: int = Field(default=100, description="Number of samples to evaluate", 
        gt=0)
    batch_size: int = Field(default=1, description="Batch size for evaluation", gt=0)
    timeout: Optional[float] = Field(
        None, description="Timeout in seconds", ge=0.0, 
            le=3600.0  # Maximum 1 hour timeout
    )

    model_config = ConfigDict(validate_assignment=True, extra="ignore", 
        str_strip_whitespace=True)


class BenchmarkResultSchema(BaseModel):
    """
    Pydantic model for benchmark result.
    """

    benchmark_name: str = Field(
        ...,
        description="Name of the benchmark",
        pattern=r"^[a - zA - Z0 - 9_\-\s]+$",  # Secure name pattern
    )
    model_id: str = Field(
        ..., description="ID of the model", 
            pattern=r"^[a - zA - Z0 - 9_\-]+$"  # Secure model ID pattern
    )
    metrics: Dict[str, float] = Field(..., description="Metric results")
    num_samples: int = Field(..., description="Number of samples evaluated", gt=0)
    execution_time: float = Field(..., description="Total execution time in seconds", 
        ge=0)
    created_at: datetime = Field(default_factory=datetime.now, 
        description="Creation timestamp")
    custom_metrics: Dict[str, Any] = Field(default_factory=dict, 
        description="Custom metrics")
    raw_data: Dict[str, Any] = Field(default_factory=dict, 
        description="Raw benchmark data")

    model_config = ConfigDict(
        validate_assignment=True,
        extra="ignore",
        str_strip_whitespace=True,
        json_schema_extra={"json_encoders": {datetime: lambda v: v.isoformat()}},
    )
