"""
Pydantic schemas for the AI Models module.

This module provides Pydantic models for data validation in the AI models module.
"""

from typing import Dict, List, Any, Optional, Union, Literal
from pydantic import BaseModel, Field, validator
from datetime import datetime
import os


class ModelConfigSchema(BaseModel):
    """
    Pydantic model for AI model configuration.
    """
    models_dir: str = Field(
        default_factory=lambda: os.path.join(os.path.expanduser("~"), ".pAIssive_income", "models"),
        description="Directory for storing AI models"
    )
    cache_dir: str = Field(
        default_factory=lambda: os.path.join(os.path.expanduser("~"), ".pAIssive_income", "cache"),
        description="Directory for caching model outputs"
    )
    cache_enabled: bool = Field(
        default=True,
        description="Whether to enable caching"
    )
    cache_ttl: int = Field(
        default=86400,  # 24 hours in seconds
        description="Time-to-live for cache entries in seconds",
        ge=0
    )
    max_cache_size: int = Field(
        default=1000,
        description="Maximum number of items in memory cache",
        gt=0
    )
    default_device: str = Field(
        default="auto",
        description="Default device for model inference (auto, cpu, cuda, mps, etc.)"
    )
    max_threads: Optional[int] = Field(
        default=None,
        description="Maximum number of threads to use (None means use all available threads)"
    )
    auto_discover: bool = Field(
        default=True,
        description="Whether to automatically discover models"
    )
    model_sources: List[str] = Field(
        default_factory=lambda: ["local", "huggingface"],
        description="Sources for model discovery"
    )
    default_text_model: str = Field(
        default="gpt2",
        description="Default text generation model"
    )
    default_embedding_model: str = Field(
        default="all-MiniLM-L6-v2",
        description="Default text embedding model"
    )

    class Config:
        """Pydantic config"""
        validate_assignment = True
        extra = "ignore"
        arbitrary_types_allowed = True

    @validator("max_threads")
    def validate_max_threads(cls, v):
        """Validate max_threads"""
        if v is not None and v <= 0:
            raise ValueError("max_threads must be positive or None")
        return v


class ModelInfoSchema(BaseModel):
    """
    Pydantic model for AI model information.
    """
    id: str = Field(..., description="Unique identifier for the model")
    name: str = Field(..., description="Name of the model")
    model_type: str = Field(..., description="Type of model (text, embedding, etc.)")
    framework: str = Field(..., description="Framework used by the model (pytorch, tensorflow, etc.)")
    path: str = Field(..., description="Path to the model files")
    description: Optional[str] = Field(None, description="Description of the model")
    version: Optional[str] = Field(None, description="Version of the model")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    class Config:
        """Pydantic config"""
        validate_assignment = True
        extra = "ignore"
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ModelParametersSchema(BaseModel):
    """
    Pydantic model for AI model parameters.
    """
    temperature: Optional[float] = Field(
        default=0.7,
        description="Temperature for sampling",
        ge=0.0,
        le=2.0
    )
    max_tokens: Optional[int] = Field(
        default=100,
        description="Maximum number of tokens to generate",
        gt=0
    )
    top_p: Optional[float] = Field(
        default=0.9,
        description="Top-p sampling parameter",
        ge=0.0,
        le=1.0
    )
    top_k: Optional[int] = Field(
        default=50,
        description="Top-k sampling parameter",
        ge=0
    )
    repetition_penalty: Optional[float] = Field(
        default=1.0,
        description="Repetition penalty",
        ge=0.0
    )
    stop_sequences: Optional[List[str]] = Field(
        default_factory=list,
        description="Sequences that stop generation"
    )
    
    class Config:
        """Pydantic config"""
        validate_assignment = True
        extra = "allow"


class TextGenerationRequestSchema(BaseModel):
    """
    Pydantic model for text generation request.
    """
    prompt: str = Field(..., description="Input prompt for text generation")
    model_id: Optional[str] = Field(None, description="ID of the model to use")
    parameters: Optional[ModelParametersSchema] = Field(
        default_factory=ModelParametersSchema,
        description="Generation parameters"
    )
    
    class Config:
        """Pydantic config"""
        validate_assignment = True
        extra = "ignore"


class TextGenerationResponseSchema(BaseModel):
    """
    Pydantic model for text generation response.
    """
    text: str = Field(..., description="Generated text")
    model_id: str = Field(..., description="ID of the model used")
    prompt: str = Field(..., description="Input prompt")
    parameters: ModelParametersSchema = Field(..., description="Generation parameters used")
    tokens_generated: int = Field(..., description="Number of tokens generated")
    generation_time: float = Field(..., description="Time taken for generation in seconds")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    
    class Config:
        """Pydantic config"""
        validate_assignment = True
        extra = "ignore"
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class EmbeddingRequestSchema(BaseModel):
    """
    Pydantic model for text embedding request.
    """
    text: Union[str, List[str]] = Field(..., description="Text to embed")
    model_id: Optional[str] = Field(None, description="ID of the model to use")
    
    class Config:
        """Pydantic config"""
        validate_assignment = True
        extra = "ignore"


class EmbeddingResponseSchema(BaseModel):
    """
    Pydantic model for text embedding response.
    """
    embeddings: List[List[float]] = Field(..., description="Text embeddings")
    model_id: str = Field(..., description="ID of the model used")
    dimensions: int = Field(..., description="Dimensions of the embeddings")
    texts: List[str] = Field(..., description="Input texts")
    embedding_time: float = Field(..., description="Time taken for embedding in seconds")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    
    class Config:
        """Pydantic config"""
        validate_assignment = True
        extra = "ignore"
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class BenchmarkConfigSchema(BaseModel):
    """
    Pydantic model for benchmark configuration.
    """
    name: str = Field(..., description="Name of the benchmark")
    description: Optional[str] = Field(None, description="Description of the benchmark")
    model_ids: List[str] = Field(..., description="IDs of models to benchmark")
    metrics: List[str] = Field(..., description="Metrics to evaluate")
    input_file: Optional[str] = Field(None, description="Path to input file")
    output_dir: str = Field(..., description="Directory for output files")
    num_samples: int = Field(default=100, description="Number of samples to evaluate", gt=0)
    batch_size: int = Field(default=1, description="Batch size for evaluation", gt=0)
    timeout: Optional[float] = Field(None, description="Timeout in seconds")
    
    class Config:
        """Pydantic config"""
        validate_assignment = True
        extra = "ignore"


class BenchmarkResultSchema(BaseModel):
    """
    Pydantic model for benchmark result.
    """
    benchmark_name: str = Field(..., description="Name of the benchmark")
    model_id: str = Field(..., description="ID of the model")
    metrics: Dict[str, float] = Field(..., description="Metric results")
    num_samples: int = Field(..., description="Number of samples evaluated")
    execution_time: float = Field(..., description="Total execution time in seconds")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    custom_metrics: Dict[str, Any] = Field(default_factory=dict, description="Custom metrics")
    raw_data: Dict[str, Any] = Field(default_factory=dict, description="Raw benchmark data")
    
    class Config:
        """Pydantic config"""
        validate_assignment = True
        extra = "ignore"
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
