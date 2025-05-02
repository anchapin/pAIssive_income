"""
Audio routes for REST API server.

This module provides route handlers for audio operations.
"""

import base64
from typing import Optional

# Try to import FastAPI
try:
    from fastapi import APIRouter, File, Form, HTTPException, UploadFile
    from fastapi.responses import StreamingResponse
    from pydantic import BaseModel, Field

    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

    # Create dummy classes for type hints
    class APIRouter:
        pass

    class BaseModel:
        pass

    Field = lambda *args, **kwargs: None
    File = lambda *args, **kwargs: None
    Form = lambda *args, **kwargs: None
    UploadFile = lambda *args, **kwargs: None


# Create router
if FASTAPI_AVAILABLE:
    router = APIRouter(prefix="/v1", tags=["Audio"])
else:
    router = None


# Define request and response models
if FASTAPI_AVAILABLE:

    class SpeechToTextRequest(BaseModel):
        """
        Request model for speech-to-text.
        """

        file: str = Field(..., description="Base64-encoded audio file")
        model: Optional[str] = Field(None, description="Model to use for transcription")
        language: Optional[str] = Field(None, description="Language of the audio")

    class SpeechToTextResponse(BaseModel):
        """
        Response model for speech-to-text.
        """

        text: str = Field(..., description="Transcribed text")

    class TextToSpeechRequest(BaseModel):
        """
        Request model for text-to-speech.
        """

        text: str = Field(..., description="Text to convert to speech")
        voice: Optional[str] = Field("default", description="Voice to use")
        response_format: str = Field("mp3", description="Format of the response (mp3 or wav)")

    class TextToSpeechResponse(BaseModel):
        """
        Response model for text-to-speech.
        """

        audio: str = Field(..., description="Base64-encoded audio data")


# Define route handlers
if FASTAPI_AVAILABLE:

    @router.post("/audio/transcriptions", response_model=SpeechToTextResponse)
    async def transcribe_audio(
        file: UploadFile = File(...),
        model: Optional[str] = Form(None),
        language: Optional[str] = Form(None),
        server_model=None,
    ):
        """
        Transcribe audio to text.

        Args:
            file: Audio file
            model: Model to use for transcription
            language: Language of the audio
            server_model: Model instance (injected by dependency)

        Returns:
            Transcribed text
        """
        if server_model is None:
            raise HTTPException(status_code=500, detail="Model not loaded")

        try:
            # Read audio file
            audio_data = await file.read()

            # Transcribe audio
            result = await _transcribe_audio(server_model, audio_data, model, language)
            return result

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.post("/audio/speech", response_model=TextToSpeechResponse)
    async def text_to_speech(request: TextToSpeechRequest, model=None):
        """
        Convert text to speech.

        Args:
            request: Text-to-speech request
            model: Model instance (injected by dependency)

        Returns:
            Generated audio
        """
        if model is None:
            raise HTTPException(status_code=500, detail="Model not loaded")

        try:
            # Generate speech
            result = await _text_to_speech(model, request)
            return result

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.post("/audio/speech/stream")
    async def text_to_speech_stream(request: TextToSpeechRequest, model=None):
        """
        Convert text to speech and stream the audio.

        Args:
            request: Text-to-speech request
            model: Model instance (injected by dependency)

        Returns:
            Streaming response with audio data
        """
        if model is None:
            raise HTTPException(status_code=500, detail="Model not loaded")

        try:
            # Generate speech
            audio_data, content_type = await _text_to_speech_raw(model, request)

            # Stream audio
            return StreamingResponse(iter([audio_data]), media_type=content_type)

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


# Helper functions
async def _transcribe_audio(model, audio_data, model_name=None, language=None):
    """
    Transcribe audio to text.

    Args:
        model: Model instance
        audio_data: Audio data
        model_name: Model to use for transcription
        language: Language of the audio

    Returns:
        Transcribed text
    """
    # Transcribe audio
    result = model.transcribe_audio(audio_data=audio_data, model=model_name, language=language)

    # Create response
    return {"text": result["text"]}


async def _text_to_speech(model, request):
    """
    Convert text to speech.

    Args:
        model: Model instance
        request: Text-to-speech request

    Returns:
        Generated audio
    """
    # Generate speech
    audio_data, _ = await _text_to_speech_raw(model, request)

    # Convert to base64
    audio_b64 = base64.b64encode(audio_data).decode("utf-8")

    # Create response
    return {"audio": audio_b64}


async def _text_to_speech_raw(model, request):
    """
    Convert text to speech and return raw audio data.

    Args:
        model: Model instance
        request: Text-to-speech request

    Returns:
        Generated audio data and content type
    """
    # Generate speech
    audio_data = model.text_to_speech(
        text=request.text, voice=request.voice, format=request.response_format
    )

    # Determine content type
    content_type = "audio/mpeg" if request.response_format == "mp3" else "audio/wav"

    return audio_data, content_type
