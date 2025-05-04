"""
"""
Text generation routes for REST API server.
Text generation routes for REST API server.


This module provides route handlers for text generation.
This module provides route handlers for text generation.
"""
"""




from typing import List, Optional
from typing import List, Optional


from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, ConfigDict, Field
from pydantic import BaseModel, ConfigDict, Field


FASTAPI_AVAILABLE
FASTAPI_AVAILABLE


# Try to import FastAPI
# Try to import FastAPI
try:
    try:
    = True
    = True
except ImportError:
except ImportError:
    FASTAPI_AVAILABLE = False
    FASTAPI_AVAILABLE = False


    # Create dummy classes for type hints
    # Create dummy classes for type hints
    class APIRouter:
    class APIRouter:
    pass
    pass


    class BaseModel:
    class BaseModel:
    pass
    pass


    def Field(*args, **kwargs):
    def Field(*args, **kwargs):
    return None
    return None




    # Create router
    # Create router
    if FASTAPI_AVAILABLE:
    if FASTAPI_AVAILABLE:
    router = APIRouter(prefix="/v1", tags=["Text Generation"])
    router = APIRouter(prefix="/v1", tags=["Text Generation"])
    else:
    else:
    router = None
    router = None




    # Define request and response models
    # Define request and response models
    if FASTAPI_AVAILABLE:
    if FASTAPI_AVAILABLE:


    class GenerationRequest(BaseModel):
    class GenerationRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=()))
    model_config = ConfigDict(protected_namespaces=()))
    """
    """
    Request model for text generation.
    Request model for text generation.
    """
    """


    prompt: str = Field(..., description="Input prompt for text generation")
    prompt: str = Field(..., description="Input prompt for text generation")
    max_tokens: int = Field(100, description="Maximum number of tokens to generate")
    max_tokens: int = Field(100, description="Maximum number of tokens to generate")
    temperature: float = Field(0.7, description="Sampling temperature")
    temperature: float = Field(0.7, description="Sampling temperature")
    top_p: float = Field(0.9, description="Nucleus sampling parameter")
    top_p: float = Field(0.9, description="Nucleus sampling parameter")
    top_k: int = Field(50, description="Top-k sampling parameter")
    top_k: int = Field(50, description="Top-k sampling parameter")
    repetition_penalty: float = Field(1.0, description="Repetition penalty")
    repetition_penalty: float = Field(1.0, description="Repetition penalty")
    stop_sequences: Optional[List[str]] = Field(
    stop_sequences: Optional[List[str]] = Field(
    None, description="Sequences that stop generation"
    None, description="Sequences that stop generation"
    )
    )
    stream: bool = Field(False, description="Whether to stream the response")
    stream: bool = Field(False, description="Whether to stream the response")


    class GenerationResponse(BaseModel):
    class GenerationResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=()))
    model_config = ConfigDict(protected_namespaces=()))
    """
    """
    Response model for text generation.
    Response model for text generation.
    """
    """


    text: str = Field(..., description="Generated text")
    text: str = Field(..., description="Generated text")
    prompt_tokens: int = Field(..., description="Number of tokens in the prompt")
    prompt_tokens: int = Field(..., description="Number of tokens in the prompt")
    completion_tokens: int = Field(
    completion_tokens: int = Field(
    ..., description="Number of tokens in the completion"
    ..., description="Number of tokens in the completion"
    )
    )
    total_tokens: int = Field(..., description="Total number of tokens")
    total_tokens: int = Field(..., description="Total number of tokens")
    finish_reason: str = Field(..., description="Reason for finishing generation")
    finish_reason: str = Field(..., description="Reason for finishing generation")


    class ChatMessage(BaseModel):
    class ChatMessage(BaseModel):
    model_config = ConfigDict(protected_namespaces=()))
    model_config = ConfigDict(protected_namespaces=()))
    """
    """
    Chat message model.
    Chat message model.
    """
    """


    role: str = Field(..., description="Role of the message sender")
    role: str = Field(..., description="Role of the message sender")
    content: str = Field(..., description="Content of the message")
    content: str = Field(..., description="Content of the message")


    class ChatRequest(BaseModel):
    class ChatRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=()))
    model_config = ConfigDict(protected_namespaces=()))
    """
    """
    Request model for chat completion.
    Request model for chat completion.
    """
    """


    messages: List[ChatMessage] = Field(..., description="List of chat messages")
    messages: List[ChatMessage] = Field(..., description="List of chat messages")
    max_tokens: int = Field(100, description="Maximum number of tokens to generate")
    max_tokens: int = Field(100, description="Maximum number of tokens to generate")
    temperature: float = Field(0.7, description="Sampling temperature")
    temperature: float = Field(0.7, description="Sampling temperature")
    top_p: float = Field(0.9, description="Nucleus sampling parameter")
    top_p: float = Field(0.9, description="Nucleus sampling parameter")
    top_k: int = Field(50, description="Top-k sampling parameter")
    top_k: int = Field(50, description="Top-k sampling parameter")
    repetition_penalty: float = Field(1.0, description="Repetition penalty")
    repetition_penalty: float = Field(1.0, description="Repetition penalty")
    stop_sequences: Optional[List[str]] = Field(
    stop_sequences: Optional[List[str]] = Field(
    None, description="Sequences that stop generation"
    None, description="Sequences that stop generation"
    )
    )
    stream: bool = Field(False, description="Whether to stream the response")
    stream: bool = Field(False, description="Whether to stream the response")


    class ChatResponse(BaseModel):
    class ChatResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=()))
    model_config = ConfigDict(protected_namespaces=()))
    """
    """
    Response model for chat completion.
    Response model for chat completion.
    """
    """


    message: ChatMessage = Field(..., description="Generated message")
    message: ChatMessage = Field(..., description="Generated message")
    prompt_tokens: int = Field(..., description="Number of tokens in the prompt")
    prompt_tokens: int = Field(..., description="Number of tokens in the prompt")
    completion_tokens: int = Field(
    completion_tokens: int = Field(
    ..., description="Number of tokens in the completion"
    ..., description="Number of tokens in the completion"
    )
    )
    total_tokens: int = Field(..., description="Total number of tokens")
    total_tokens: int = Field(..., description="Total number of tokens")
    finish_reason: str = Field(..., description="Reason for finishing generation")
    finish_reason: str = Field(..., description="Reason for finishing generation")




    # Define route handlers
    # Define route handlers
    if FASTAPI_AVAILABLE:
    if FASTAPI_AVAILABLE:


    @router.post("/completions", response_model=GenerationResponse)
    @router.post("/completions", response_model=GenerationResponse)
    async def generate_text(request: GenerationRequest, model=None):
    async def generate_text(request: GenerationRequest, model=None):
    """
    """
    Generate text from a prompt.
    Generate text from a prompt.


    Args:
    Args:
    request: Generation request
    request: Generation request
    model: Model instance (injected by dependency)
    model: Model instance (injected by dependency)


    Returns:
    Returns:
    Generated text
    Generated text
    """
    """
    if model is None:
    if model is None:
    raise HTTPException(status_code=500, detail="Model not loaded")
    raise HTTPException(status_code=500, detail="Model not loaded")


    try:
    try:
    # Generate text
    # Generate text
    if request.stream:
    if request.stream:
    return StreamingResponse(
    return StreamingResponse(
    _stream_text_generation(model, request),
    _stream_text_generation(model, request),
    media_type="text/event-stream",
    media_type="text/event-stream",
    )
    )


    # Generate text (non-streaming)
    # Generate text (non-streaming)
    result = await _generate_text(model, request)
    result = await _generate_text(model, request)
    return result
    return result


except Exception as e:
except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))
    raise HTTPException(status_code=500, detail=str(e))


    @router.post("/chat/completions", response_model=ChatResponse)
    @router.post("/chat/completions", response_model=ChatResponse)
    async def generate_chat_completion(request: ChatRequest, model=None):
    async def generate_chat_completion(request: ChatRequest, model=None):
    """
    """
    Generate a chat completion.
    Generate a chat completion.


    Args:
    Args:
    request: Chat request
    request: Chat request
    model: Model instance (injected by dependency)
    model: Model instance (injected by dependency)


    Returns:
    Returns:
    Generated chat completion
    Generated chat completion
    """
    """
    if model is None:
    if model is None:
    raise HTTPException(status_code=500, detail="Model not loaded")
    raise HTTPException(status_code=500, detail="Model not loaded")


    try:
    try:
    # Generate chat completion
    # Generate chat completion
    if request.stream:
    if request.stream:
    return StreamingResponse(
    return StreamingResponse(
    _stream_chat_completion(model, request),
    _stream_chat_completion(model, request),
    media_type="text/event-stream",
    media_type="text/event-stream",
    )
    )


    # Generate chat completion (non-streaming)
    # Generate chat completion (non-streaming)
    result = await _generate_chat_completion(model, request)
    result = await _generate_chat_completion(model, request)
    return result
    return result


except Exception as e:
except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))
    raise HTTPException(status_code=500, detail=str(e))




    # Helper functions
    # Helper functions
    async def _generate_text(model, request):
    async def _generate_text(model, request):
    """
    """
    Generate text from a prompt.
    Generate text from a prompt.


    Args:
    Args:
    model: Model instance
    model: Model instance
    request: Generation request
    request: Generation request


    Returns:
    Returns:
    Generated text
    Generated text
    """
    """
    # Get generation parameters
    # Get generation parameters
    params = {
    params = {
    "max_tokens": request.max_tokens,
    "max_tokens": request.max_tokens,
    "temperature": request.temperature,
    "temperature": request.temperature,
    "top_p": request.top_p,
    "top_p": request.top_p,
    "top_k": request.top_k,
    "top_k": request.top_k,
    "repetition_penalty": request.repetition_penalty,
    "repetition_penalty": request.repetition_penalty,
    "stop_sequences": request.stop_sequences,
    "stop_sequences": request.stop_sequences,
    }
    }


    # Generate text
    # Generate text
    result = model.generate_text(request.prompt, **params)
    result = model.generate_text(request.prompt, **params)


    # Count tokens
    # Count tokens
    prompt_tokens = model.count_tokens(request.prompt)
    prompt_tokens = model.count_tokens(request.prompt)
    completion_tokens = model.count_tokens(result["text"])
    completion_tokens = model.count_tokens(result["text"])


    # Create response
    # Create response
    return {
    return {
    "text": result["text"],
    "text": result["text"],
    "prompt_tokens": prompt_tokens,
    "prompt_tokens": prompt_tokens,
    "completion_tokens": completion_tokens,
    "completion_tokens": completion_tokens,
    "total_tokens": prompt_tokens + completion_tokens,
    "total_tokens": prompt_tokens + completion_tokens,
    "finish_reason": result.get("finish_reason", "stop"),
    "finish_reason": result.get("finish_reason", "stop"),
    }
    }




    async def _stream_text_generation(model, request):
    async def _stream_text_generation(model, request):
    """
    """
    Stream text generation.
    Stream text generation.


    Args:
    Args:
    model: Model instance
    model: Model instance
    request: Generation request
    request: Generation request


    Yields:
    Yields:
    Generated text chunks
    Generated text chunks
    """
    """
    # Get generation parameters
    # Get generation parameters
    params = {
    params = {
    "max_tokens": request.max_tokens,
    "max_tokens": request.max_tokens,
    "temperature": request.temperature,
    "temperature": request.temperature,
    "top_p": request.top_p,
    "top_p": request.top_p,
    "top_k": request.top_k,
    "top_k": request.top_k,
    "repetition_penalty": request.repetition_penalty,
    "repetition_penalty": request.repetition_penalty,
    "stop_sequences": request.stop_sequences,
    "stop_sequences": request.stop_sequences,
    "stream": True,
    "stream": True,
    }
    }


    # Count prompt tokens
    # Count prompt tokens
    prompt_tokens = model.count_tokens(request.prompt)
    prompt_tokens = model.count_tokens(request.prompt)
    completion_tokens = 0
    completion_tokens = 0


    # Stream text generation
    # Stream text generation
    for chunk in model.generate_text_stream(request.prompt, **params):
    for chunk in model.generate_text_stream(request.prompt, **params):
    completion_tokens += 1
    completion_tokens += 1


    # Create response chunk
    # Create response chunk
    response = {
    response = {
    "text": chunk["text"],
    "text": chunk["text"],
    "prompt_tokens": prompt_tokens,
    "prompt_tokens": prompt_tokens,
    "completion_tokens": completion_tokens,
    "completion_tokens": completion_tokens,
    "total_tokens": prompt_tokens + completion_tokens,
    "total_tokens": prompt_tokens + completion_tokens,
    "finish_reason": chunk.get("finish_reason", None),
    "finish_reason": chunk.get("finish_reason", None),
    }
    }


    # Yield response chunk
    # Yield response chunk
    yield f"data: {response}\n\n"
    yield f"data: {response}\n\n"


    # End the stream
    # End the stream
    yield "data: [DONE]\n\n"
    yield "data: [DONE]\n\n"




    async def _generate_chat_completion(model, request):
    async def _generate_chat_completion(model, request):
    """
    """
    Generate a chat completion.
    Generate a chat completion.


    Args:
    Args:
    model: Model instance
    model: Model instance
    request: Chat request
    request: Chat request


    Returns:
    Returns:
    Generated chat completion
    Generated chat completion
    """
    """
    # Get generation parameters
    # Get generation parameters
    params = {
    params = {
    "max_tokens": request.max_tokens,
    "max_tokens": request.max_tokens,
    "temperature": request.temperature,
    "temperature": request.temperature,
    "top_p": request.top_p,
    "top_p": request.top_p,
    "top_k": request.top_k,
    "top_k": request.top_k,
    "repetition_penalty": request.repetition_penalty,
    "repetition_penalty": request.repetition_penalty,
    "stop_sequences": request.stop_sequences,
    "stop_sequences": request.stop_sequences,
    }
    }


    # Generate chat completion
    # Generate chat completion
    result = model.generate_chat_completion(request.messages, **params)
    result = model.generate_chat_completion(request.messages, **params)


    # Count tokens
    # Count tokens
    prompt_tokens = model.count_tokens_from_messages(request.messages)
    prompt_tokens = model.count_tokens_from_messages(request.messages)
    completion_tokens = model.count_tokens(result["message"]["content"])
    completion_tokens = model.count_tokens(result["message"]["content"])


    # Create response
    # Create response
    return {
    return {
    "message": result["message"],
    "message": result["message"],
    "prompt_tokens": prompt_tokens,
    "prompt_tokens": prompt_tokens,
    "completion_tokens": completion_tokens,
    "completion_tokens": completion_tokens,
    "total_tokens": prompt_tokens + completion_tokens,
    "total_tokens": prompt_tokens + completion_tokens,
    "finish_reason": result.get("finish_reason", "stop"),
    "finish_reason": result.get("finish_reason", "stop"),
    }
    }




    async def _stream_chat_completion(model, request):
    async def _stream_chat_completion(model, request):
    """
    """
    Stream chat completion.
    Stream chat completion.


    Args:
    Args:
    model: Model instance
    model: Model instance
    request: Chat request
    request: Chat request


    Yields:
    Yields:
    Generated chat completion chunks
    Generated chat completion chunks
    """
    """
    # Get generation parameters
    # Get generation parameters
    params = {
    params = {
    "max_tokens": request.max_tokens,
    "max_tokens": request.max_tokens,
    "temperature": request.temperature,
    "temperature": request.temperature,
    "top_p": request.top_p,
    "top_p": request.top_p,
    "top_k": request.top_k,
    "top_k": request.top_k,
    "repetition_penalty": request.repetition_penalty,
    "repetition_penalty": request.repetition_penalty,
    "stop_sequences": request.stop_sequences,
    "stop_sequences": request.stop_sequences,
    "stream": True,
    "stream": True,
    }
    }


    # Count prompt tokens
    # Count prompt tokens
    prompt_tokens = model.count_tokens_from_messages(request.messages)
    prompt_tokens = model.count_tokens_from_messages(request.messages)
    completion_tokens = 0
    completion_tokens = 0


    # Stream chat completion
    # Stream chat completion
    for chunk in model.generate_chat_completion_stream(request.messages, **params:
    for chunk in model.generate_chat_completion_stream(request.messages, **params:
    completion_tokens += 1
    completion_tokens += 1


    # Create response chunk
    # Create response chunk
    response = {
    response = {
    "message": {"role": "assistant", "content": chunk["content"]},
    "message": {"role": "assistant", "content": chunk["content"]},
    "prompt_tokens": prompt_tokens,
    "prompt_tokens": prompt_tokens,
    "completion_tokens": completion_tokens,
    "completion_tokens": completion_tokens,
    "total_tokens": prompt_tokens + completion_tokens,
    "total_tokens": prompt_tokens + completion_tokens,
    "finish_reason": chunk.get("finish_reason", None,
    "finish_reason": chunk.get("finish_reason", None,
    }
    }


    # Yield response chunk
    # Yield response chunk
    yield f"data: {response}\n\n"
    yield f"data: {response}\n\n"


    # End the stream
    # End the stream
    yield "data: [DONE]\n\n"
    yield "data: [DONE]\n\n"