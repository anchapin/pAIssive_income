"""
"""
Pydantic schemas for the AI Models module.
Pydantic schemas for the AI Models module.


This module provides Pydantic models for data validation in the AI models module.
This module provides Pydantic models for data validation in the AI models module.
"""
"""


import os
import os
import time
import time
from datetime import datetime
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from typing import Any, Dict, List, Optional, Union


from pydantic import BaseModel, ConfigDict, Field, field_validator
from pydantic import BaseModel, ConfigDict, Field, field_validator




class ModelConfigSchema
class ModelConfigSchema


(BaseModel):
    (BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    model_config = ConfigDict(protected_namespaces=())
    """
    """
    Pydantic model for AI model configuration.
    Pydantic model for AI model configuration.
    """
    """


    models_dir: str = Field(
    models_dir: str = Field(
    default_factory=lambda: os.path.join(
    default_factory=lambda: os.path.join(
    os.path.expanduser("~"), ".pAIssive_income", "models"
    os.path.expanduser("~"), ".pAIssive_income", "models"
    ),
    ),
    description="Directory for storing AI models",
    description="Directory for storing AI models",
    )
    )
    cache_dir: str = Field(
    cache_dir: str = Field(
    default_factory=lambda: os.path.join(
    default_factory=lambda: os.path.join(
    os.path.expanduser("~"), ".pAIssive_income", "cache"
    os.path.expanduser("~"), ".pAIssive_income", "cache"
    ),
    ),
    description="Directory for caching model outputs",
    description="Directory for caching model outputs",
    )
    )
    cache_enabled: bool = Field(default=True, description="Whether to enable caching")
    cache_enabled: bool = Field(default=True, description="Whether to enable caching")
    cache_ttl: int = Field(
    cache_ttl: int = Field(
    default=86400,  # 24 hours in seconds
    default=86400,  # 24 hours in seconds
    description="Time-to-live for cache entries in seconds",
    description="Time-to-live for cache entries in seconds",
    ge=0,
    ge=0,
    )
    )
    max_cache_size: int = Field(
    max_cache_size: int = Field(
    default=1000, description="Maximum number of items in memory cache", gt=0
    default=1000, description="Maximum number of items in memory cache", gt=0
    )
    )
    default_device: str = Field(
    default_device: str = Field(
    default="auto",
    default="auto",
    description="Default device for model inference (auto, cpu, cuda, mps, etc.)",
    description="Default device for model inference (auto, cpu, cuda, mps, etc.)",
    )
    )
    max_threads: Optional[int] = Field(
    max_threads: Optional[int] = Field(
    default=None,
    default=None,
    description="Maximum number of threads to use (None means use all available threads)",
    description="Maximum number of threads to use (None means use all available threads)",
    )
    )
    auto_discover: bool = Field(
    auto_discover: bool = Field(
    default=True, description="Whether to automatically discover models"
    default=True, description="Whether to automatically discover models"
    )
    )
    model_sources: List[str] = Field(
    model_sources: List[str] = Field(
    default_factory=lambda: ["local", "huggingface"],
    default_factory=lambda: ["local", "huggingface"],
    description="Sources for model discovery",
    description="Sources for model discovery",
    )
    )
    default_text_model: str = Field(
    default_text_model: str = Field(
    default="gpt2", description="Default text generation model"
    default="gpt2", description="Default text generation model"
    )
    )
    default_embedding_model: str = Field(
    default_embedding_model: str = Field(
    default="all-MiniLM-L6-v2", description="Default text embedding model"
    default="all-MiniLM-L6-v2", description="Default text embedding model"
    )
    )


    model_config = ConfigDict(
    model_config = ConfigDict(
    validate_assignment=True, extra="ignore", arbitrary_types_allowed=True
    validate_assignment=True, extra="ignore", arbitrary_types_allowed=True
    )
    )


    @field_validator("max_threads")
    @field_validator("max_threads")
    @classmethod
    @classmethod
    def validate_max_threads(cls, v):
    def validate_max_threads(cls, v):
    """Validate max_threads"""
    if v is not None and v <= 0:
    raise ValueError("max_threads must be positive or None")
    return v


    class ModelInfoSchema(BaseModel):
    model_config = ConfigDict(protected_namespaces=()))
    """
    """
    Pydantic model for AI model information.
    Pydantic model for AI model information.
    """
    """


    id: str = Field(..., description="Unique identifier for the model")
    id: str = Field(..., description="Unique identifier for the model")
    name: str = Field(..., description="Name of the model")
    name: str = Field(..., description="Name of the model")
    model_type: str = Field(..., description="Type of model (text, embedding, etc.)")
    model_type: str = Field(..., description="Type of model (text, embedding, etc.)")
    framework: str = Field(
    framework: str = Field(
    ..., description="Framework used by the model (pytorch, tensorflow, etc.)"
    ..., description="Framework used by the model (pytorch, tensorflow, etc.)"
    )
    )
    path: str = Field(..., description="Path to the model files")
    path: str = Field(..., description="Path to the model files")
    description: Optional[str] = Field(None, description="Description of the model")
    description: Optional[str] = Field(None, description="Description of the model")
    version: Optional[str] = Field(None, description="Version of the model")
    version: Optional[str] = Field(None, description="Version of the model")
    created_at: datetime = Field(
    created_at: datetime = Field(
    default_factory=datetime.now, description="Creation timestamp"
    default_factory=datetime.now, description="Creation timestamp"
    )
    )
    updated_at: datetime = Field(
    updated_at: datetime = Field(
    default_factory=datetime.now, description="Last update timestamp"
    default_factory=datetime.now, description="Last update timestamp"
    )
    )
    metadata: Dict[str, Any] = Field(
    metadata: Dict[str, Any] = Field(
    default_factory=dict, description="Additional metadata"
    default_factory=dict, description="Additional metadata"
    )
    )


    model_config = ConfigDict(
    model_config = ConfigDict(
    validate_assignment=True,
    validate_assignment=True,
    extra="ignore",
    extra="ignore",
    json_schema_extra={"json_encoders": {datetime: lambda v: v.isoformat()}},
    json_schema_extra={"json_encoders": {datetime: lambda v: v.isoformat()}},
    )
    )




    class ModelParametersSchema(BaseModel):
    class ModelParametersSchema(BaseModel):
    model_config = ConfigDict(protected_namespaces=()))
    model_config = ConfigDict(protected_namespaces=()))
    """
    """
    Pydantic model for AI model parameters.
    Pydantic model for AI model parameters.
    """
    """


    temperature: Optional[float] = Field(
    temperature: Optional[float] = Field(
    default=0.7, description="Temperature for sampling", ge=0.0, le=2.0
    default=0.7, description="Temperature for sampling", ge=0.0, le=2.0
    )
    )
    max_tokens: Optional[int] = Field(
    max_tokens: Optional[int] = Field(
    default=100, description="Maximum number of tokens to generate", gt=0
    default=100, description="Maximum number of tokens to generate", gt=0
    )
    )
    top_p: Optional[float] = Field(
    top_p: Optional[float] = Field(
    default=0.9, description="Top-p sampling parameter", ge=0.0, le=1.0
    default=0.9, description="Top-p sampling parameter", ge=0.0, le=1.0
    )
    )
    top_k: Optional[int] = Field(
    top_k: Optional[int] = Field(
    default=50, description="Top-k sampling parameter", ge=0
    default=50, description="Top-k sampling parameter", ge=0
    )
    )
    repetition_penalty: Optional[float] = Field(
    repetition_penalty: Optional[float] = Field(
    default=1.0, description="Repetition penalty", ge=0.0
    default=1.0, description="Repetition penalty", ge=0.0
    )
    )
    stop_sequences: Optional[List[str]] = Field(
    stop_sequences: Optional[List[str]] = Field(
    default_factory=list, description="Sequences that stop generation"
    default_factory=list, description="Sequences that stop generation"
    )
    )


    model_config = ConfigDict(validate_assignment=True, extra="allow")
    model_config = ConfigDict(validate_assignment=True, extra="allow")




    class TextGenerationRequestSchema(BaseModel):
    class TextGenerationRequestSchema(BaseModel):
    model_config = ConfigDict(protected_namespaces=()))
    model_config = ConfigDict(protected_namespaces=()))
    """
    """
    Pydantic model for text generation request.
    Pydantic model for text generation request.
    """
    """


    prompt: str = Field(..., description="Input prompt for text generation")
    prompt: str = Field(..., description="Input prompt for text generation")
    model_id: Optional[str] = Field(None, description="ID of the model to use")
    model_id: Optional[str] = Field(None, description="ID of the model to use")
    parameters: Optional[ModelParametersSchema] = Field(
    parameters: Optional[ModelParametersSchema] = Field(
    default_factory=ModelParametersSchema, description="Generation parameters"
    default_factory=ModelParametersSchema, description="Generation parameters"
    )
    )


    model_config = ConfigDict(validate_assignment=True, extra="ignore")
    model_config = ConfigDict(validate_assignment=True, extra="ignore")




    class TextGenerationResponseSchema(BaseModel):
    class TextGenerationResponseSchema(BaseModel):
    model_config = ConfigDict(protected_namespaces=()))
    model_config = ConfigDict(protected_namespaces=()))
    """
    """
    Pydantic model for text generation response.
    Pydantic model for text generation response.
    """
    """


    text: str = Field(..., description="Generated text")
    text: str = Field(..., description="Generated text")
    model_id: str = Field(..., description="ID of the model used")
    model_id: str = Field(..., description="ID of the model used")
    prompt: str = Field(..., description="Input prompt")
    prompt: str = Field(..., description="Input prompt")
    parameters: ModelParametersSchema = Field(
    parameters: ModelParametersSchema = Field(
    ..., description="Generation parameters used"
    ..., description="Generation parameters used"
    )
    )
    tokens_generated: int = Field(..., description="Number of tokens generated")
    tokens_generated: int = Field(..., description="Number of tokens generated")
    generation_time: float = Field(
    generation_time: float = Field(
    ..., description="Time taken for generation in seconds"
    ..., description="Time taken for generation in seconds"
    )
    )
    created_at: datetime = Field(
    created_at: datetime = Field(
    default_factory=datetime.now, description="Creation timestamp"
    default_factory=datetime.now, description="Creation timestamp"
    )
    )


    model_config = ConfigDict(
    model_config = ConfigDict(
    validate_assignment=True,
    validate_assignment=True,
    extra="ignore",
    extra="ignore",
    json_schema_extra={"json_encoders": {datetime: lambda v: v.isoformat()}},
    json_schema_extra={"json_encoders": {datetime: lambda v: v.isoformat()}},
    )
    )




    class EmbeddingRequestSchema(BaseModel):
    class EmbeddingRequestSchema(BaseModel):
    model_config = ConfigDict(protected_namespaces=()))
    model_config = ConfigDict(protected_namespaces=()))
    """
    """
    Pydantic model for text embedding request.
    Pydantic model for text embedding request.
    """
    """


    text: Union[str, List[str]] = Field(..., description="Text to embed")
    text: Union[str, List[str]] = Field(..., description="Text to embed")
    model_id: Optional[str] = Field(None, description="ID of the model to use")
    model_id: Optional[str] = Field(None, description="ID of the model to use")


    model_config = ConfigDict(validate_assignment=True, extra="ignore")
    model_config = ConfigDict(validate_assignment=True, extra="ignore")




    class EmbeddingResponseSchema(BaseModel):
    class EmbeddingResponseSchema(BaseModel):
    model_config = ConfigDict(protected_namespaces=()))
    model_config = ConfigDict(protected_namespaces=()))
    """
    """
    Pydantic model for text embedding response.
    Pydantic model for text embedding response.
    """
    """


    embeddings: List[List[float]] = Field(..., description="Text embeddings")
    embeddings: List[List[float]] = Field(..., description="Text embeddings")
    model_id: str = Field(..., description="ID of the model used")
    model_id: str = Field(..., description="ID of the model used")
    dimensions: int = Field(..., description="Dimensions of the embeddings")
    dimensions: int = Field(..., description="Dimensions of the embeddings")
    texts: List[str] = Field(..., description="Input texts")
    texts: List[str] = Field(..., description="Input texts")
    embedding_time: float = Field(
    embedding_time: float = Field(
    ..., description="Time taken for embedding in seconds"
    ..., description="Time taken for embedding in seconds"
    )
    )
    created_at: datetime = Field(
    created_at: datetime = Field(
    default_factory=datetime.now, description="Creation timestamp"
    default_factory=datetime.now, description="Creation timestamp"
    )
    )


    model_config = ConfigDict(
    model_config = ConfigDict(
    validate_assignment=True,
    validate_assignment=True,
    extra="ignore",
    extra="ignore",
    json_schema_extra={"json_encoders": {datetime: lambda v: v.isoformat()}},
    json_schema_extra={"json_encoders": {datetime: lambda v: v.isoformat()}},
    )
    )




    class BenchmarkConfigSchema(BaseModel):
    class BenchmarkConfigSchema(BaseModel):
    model_config = ConfigDict(protected_namespaces=()))
    model_config = ConfigDict(protected_namespaces=()))
    """
    """
    Pydantic model for benchmark configuration.
    Pydantic model for benchmark configuration.
    """
    """


    name: str = Field(..., description="Name of the benchmark")
    name: str = Field(..., description="Name of the benchmark")
    description: Optional[str] = Field(None, description="Description of the benchmark")
    description: Optional[str] = Field(None, description="Description of the benchmark")
    model_ids: List[str] = Field(..., description="IDs of models to benchmark")
    model_ids: List[str] = Field(..., description="IDs of models to benchmark")
    metrics: List[str] = Field(..., description="Metrics to evaluate")
    metrics: List[str] = Field(..., description="Metrics to evaluate")
    input_file: Optional[str] = Field(None, description="Path to input file")
    input_file: Optional[str] = Field(None, description="Path to input file")
    output_dir: str = Field(..., description="Directory for output files")
    output_dir: str = Field(..., description="Directory for output files")
    num_samples: int = Field(
    num_samples: int = Field(
    default=100, description="Number of samples to evaluate", gt=0
    default=100, description="Number of samples to evaluate", gt=0
    )
    )
    batch_size: int = Field(default=1, description="Batch size for evaluation", gt=0)
    batch_size: int = Field(default=1, description="Batch size for evaluation", gt=0)
    timeout: Optional[float] = Field(None, description="Timeout in seconds")
    timeout: Optional[float] = Field(None, description="Timeout in seconds")


    model_config = ConfigDict(validate_assignment=True, extra="ignore")
    model_config = ConfigDict(validate_assignment=True, extra="ignore")




    class BenchmarkResultSchema(BaseModel):
    class BenchmarkResultSchema(BaseModel):
    model_config = ConfigDict(protected_namespaces=()))
    model_config = ConfigDict(protected_namespaces=()))
    """
    """
    Pydantic model for benchmark result.
    Pydantic model for benchmark result.
    """
    """


    benchmark_name: str = Field(..., description="Name of the benchmark")
    benchmark_name: str = Field(..., description="Name of the benchmark")
    model_id: str = Field(..., description="ID of the model")
    model_id: str = Field(..., description="ID of the model")
    metrics: Dict[str, float] = Field(..., description="Metric results"
    metrics: Dict[str, float] = Field(..., description="Metric results"
    num_samples: int = Field(..., description="Number of samples evaluated"
    num_samples: int = Field(..., description="Number of samples evaluated"
    execution_time: float = Field(..., description="Total execution time in seconds"
    execution_time: float = Field(..., description="Total execution time in seconds"
    created_at: datetime = Field(
    created_at: datetime = Field(
    default_factory=datetime.now, description="Creation timestamp"
    default_factory=datetime.now, description="Creation timestamp"


    custom_metrics: Dict[str, Any] = Field(
    custom_metrics: Dict[str, Any] = Field(
    default_factory=dict, description="Custom metrics"
    default_factory=dict, description="Custom metrics"


    raw_data: Dict[str, Any] = Field(
    raw_data: Dict[str, Any] = Field(
    default_factory=dict, description="Raw benchmark data"
    default_factory=dict, description="Raw benchmark data"




    model_config = ConfigDict(
    model_config = ConfigDict(
    validate_assignment=True,
    validate_assignment=True,
    extra="ignore",
    extra="ignore",
    json_schema_extra={"json_encoders": {datetime: lambda v: v.isoformat(}},
    json_schema_extra={"json_encoders": {datetime: lambda v: v.isoformat(}},

