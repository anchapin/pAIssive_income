"""
Text generation routes for REST API server.

This module provides route handlers for text generation.
"""

from typing import List, Optional

# Try to import FastAPI
try:
    from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
    from fastapi.responses import StreamingResponse
    from pydantic import BaseModel, ConfigDict, Field

    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

    # Create dummy classes for type hints
    class APIRouter:
        pass

    class BaseModel:
        pass

    def Field(*args, **kwargs):
        return None


# Create router
if FASTAPI_AVAILABLE:
    router = APIRouter(prefix="/v1", tags=["Text Generation"])
else:
    router = None


# Define request and response models
if FASTAPI_AVAILABLE:

    class GenerationRequest(BaseModel):
        model_config = ConfigDict(protected_namespaces=())
        """
        Request model for text generation.
        """

        prompt: str = Field(..., description="Input prompt for text generation")
        max_tokens: int = Field(100, description="Maximum number of tokens to generate")
        temperature: float = Field(0.7, description="Sampling temperature")
        top_p: float = Field(0.9, description="Nucleus sampling parameter")
        top_k: int = Field(50, description="Top-k sampling parameter")
        repetition_penalty: float = Field(1.0, description="Repetition penalty")
        stop_sequences: Optional[List[str]] = Field(
            None, description="Sequences that stop generation"
        )
        stream: bool = Field(False, description="Whether to stream the response")

    class GenerationResponse(BaseModel):
        model_config = ConfigDict(protected_namespaces=())
        """
        Response model for text generation.
        """

        text: str = Field(..., description="Generated text")
        prompt_tokens: int = Field(..., description="Number of tokens in the prompt")
        completion_tokens: int = Field(
            ..., description="Number of tokens in the completion"
        )
        total_tokens: int = Field(..., description="Total number of tokens")
        finish_reason: str = Field(..., description="Reason for finishing generation")

    class ChatMessage(BaseModel):
        model_config = ConfigDict(protected_namespaces=())
        """
        Chat message model.
        """

        role: str = Field(..., description="Role of the message sender")
        content: str = Field(..., description="Content of the message")

    class ChatRequest(BaseModel):
        model_config = ConfigDict(protected_namespaces=())
        """
        Request model for chat completion.
        """

        messages: List[ChatMessage] = Field(..., description="List of chat messages")
        max_tokens: int = Field(100, description="Maximum number of tokens to generate")
        temperature: float = Field(0.7, description="Sampling temperature")
        top_p: float = Field(0.9, description="Nucleus sampling parameter")
        top_k: int = Field(50, description="Top-k sampling parameter")
        repetition_penalty: float = Field(1.0, description="Repetition penalty")
        stop_sequences: Optional[List[str]] = Field(
            None, description="Sequences that stop generation"
        )
        stream: bool = Field(False, description="Whether to stream the response")

    class ChatResponse(BaseModel):
        model_config = ConfigDict(protected_namespaces=())
        """
        Response model for chat completion.
        """

        message: ChatMessage = Field(..., description="Generated message")
        prompt_tokens: int = Field(..., description="Number of tokens in the prompt")
        completion_tokens: int = Field(
            ..., description="Number of tokens in the completion"
        )
        total_tokens: int = Field(..., description="Total number of tokens")
        finish_reason: str = Field(..., description="Reason for finishing generation")


# Define route handlers
if FASTAPI_AVAILABLE:

    @router.post("/completions", response_model=GenerationResponse)
    async def generate_text(request: GenerationRequest, model=None):
        """
        Generate text from a prompt.

        Args:
            request: Generation request
            model: Model instance (injected by dependency)

        Returns:
            Generated text
        """
        if model is None:
            raise HTTPException(status_code=500, detail="Model not loaded")

        try:
            # Generate text
            if request.stream:
                return StreamingResponse(
                    _stream_text_generation(model, request),
                    media_type="text/event-stream",
                )

            # Generate text (non-streaming)
            result = await _generate_text(model, request)
            return result

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.post("/chat/completions", response_model=ChatResponse)
    async def generate_chat_completion(request: ChatRequest, model=None):
        """
        Generate a chat completion.

        Args:
            request: Chat request
            model: Model instance (injected by dependency)

        Returns:
            Generated chat completion
        """
        if model is None:
            raise HTTPException(status_code=500, detail="Model not loaded")

        try:
            # Generate chat completion
            if request.stream:
                return StreamingResponse(
                    _stream_chat_completion(model, request),
                    media_type="text/event-stream",
                )

            # Generate chat completion (non-streaming)
            result = await _generate_chat_completion(model, request)
            return result

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


# Helper functions
async def _generate_text(model, request):
    """
    Generate text from a prompt.

    Args:
        model: Model instance
        request: Generation request

    Returns:
        Generated text
    """
    # Get generation parameters
    params = {
        "max_tokens": request.max_tokens,
        "temperature": request.temperature,
        "top_p": request.top_p,
        "top_k": request.top_k,
        "repetition_penalty": request.repetition_penalty,
        "stop_sequences": request.stop_sequences,
    }

    # Generate text
    result = model.generate_text(request.prompt, **params)

    # Count tokens
    prompt_tokens = model.count_tokens(request.prompt)
    completion_tokens = model.count_tokens(result["text"])

    # Create response
    return {
        "text": result["text"],
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": prompt_tokens + completion_tokens,
        "finish_reason": result.get("finish_reason", "stop"),
    }


async def _stream_text_generation(model, request):
    """
    Stream text generation.

    Args:
        model: Model instance
        request: Generation request

    Yields:
        Generated text chunks
    """
    # Get generation parameters
    params = {
        "max_tokens": request.max_tokens,
        "temperature": request.temperature,
        "top_p": request.top_p,
        "top_k": request.top_k,
        "repetition_penalty": request.repetition_penalty,
        "stop_sequences": request.stop_sequences,
        "stream": True,
    }

    # Count prompt tokens
    prompt_tokens = model.count_tokens(request.prompt)
    completion_tokens = 0

    # Stream text generation
    for chunk in model.generate_text_stream(request.prompt, **params):
        completion_tokens += 1

        # Create response chunk
        response = {
            "text": chunk["text"],
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
            "finish_reason": chunk.get("finish_reason", None),
        }

        # Yield response chunk
        yield f"data: {response}\n\n"

    # End the stream
    yield "data: [DONE]\n\n"


async def _generate_chat_completion(model, request):
    """
    Generate a chat completion.

    Args:
        model: Model instance
        request: Chat request

    Returns:
        Generated chat completion
    """
    # Get generation parameters
    params = {
        "max_tokens": request.max_tokens,
        "temperature": request.temperature,
        "top_p": request.top_p,
        "top_k": request.top_k,
        "repetition_penalty": request.repetition_penalty,
        "stop_sequences": request.stop_sequences,
    }

    # Generate chat completion
    result = model.generate_chat_completion(request.messages, **params)

    # Count tokens
    prompt_tokens = model.count_tokens_from_messages(request.messages)
    completion_tokens = model.count_tokens(result["message"]["content"])

    # Create response
    return {
        "message": result["message"],
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": prompt_tokens + completion_tokens,
        "finish_reason": result.get("finish_reason", "stop"),
    }


async def _stream_chat_completion(model, request):
    """
    Stream chat completion.

    Args:
        model: Model instance
        request: Chat request

    Yields:
        Generated chat completion chunks
    """
    # Get generation parameters
    params = {
        "max_tokens": request.max_tokens,
        "temperature": request.temperature,
        "top_p": request.top_p,
        "top_k": request.top_k,
        "repetition_penalty": request.repetition_penalty,
        "stop_sequences": request.stop_sequences,
        "stream": True,
    }

    # Count prompt tokens
    prompt_tokens = model.count_tokens_from_messages(request.messages)
    completion_tokens = 0

    # Stream chat completion
    for chunk in model.generate_chat_completion_stream(request.messages, **params):
        completion_tokens += 1

        # Create response chunk
        response = {
            "message": {"role": "assistant", "content": chunk["content"]},
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
            "finish_reason": chunk.get("finish_reason", None),
        }

        # Yield response chunk
        yield f"data: {response}\n\n"

    # End the stream
    yield "data: [DONE]\n\n"
