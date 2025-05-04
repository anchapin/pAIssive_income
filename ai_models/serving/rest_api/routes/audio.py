"""
"""
Audio routes for REST API server.
Audio routes for REST API server.


This module provides route handlers for audio operations.
This module provides route handlers for audio operations.
"""
"""




import base64
import base64
from typing import Optional
from typing import Optional


from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import Response, StreamingResponse
from fastapi.responses import Response, StreamingResponse
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
    def File(*args, **kwargs):
    def File(*args, **kwargs):
    return None
    return None
    def Form(*args, **kwargs):
    def Form(*args, **kwargs):
    return None
    return None
    def UploadFile(*args, **kwargs):
    def UploadFile(*args, **kwargs):
    return None
    return None




    # Create router
    # Create router
    if FASTAPI_AVAILABLE:
    if FASTAPI_AVAILABLE:
    router = APIRouter(prefix="/v1", tags=["Audio"])
    router = APIRouter(prefix="/v1", tags=["Audio"])
    else:
    else:
    router = None
    router = None




    # Define request and response models
    # Define request and response models
    if FASTAPI_AVAILABLE:
    if FASTAPI_AVAILABLE:


    class SpeechToTextRequest(BaseModel):
    class SpeechToTextRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=()))
    model_config = ConfigDict(protected_namespaces=()))
    """
    """
    Request model for speech-to-text.
    Request model for speech-to-text.
    """
    """


    file: str = Field(..., description="Base64-encoded audio file")
    file: str = Field(..., description="Base64-encoded audio file")
    model: Optional[str] = Field(None, description="Model to use for transcription")
    model: Optional[str] = Field(None, description="Model to use for transcription")
    language: Optional[str] = Field(None, description="Language of the audio")
    language: Optional[str] = Field(None, description="Language of the audio")


    class SpeechToTextResponse(BaseModel):
    class SpeechToTextResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=()))
    model_config = ConfigDict(protected_namespaces=()))
    """
    """
    Response model for speech-to-text.
    Response model for speech-to-text.
    """
    """


    text: str = Field(..., description="Transcribed text")
    text: str = Field(..., description="Transcribed text")


    class TextToSpeechRequest(BaseModel):
    class TextToSpeechRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=()))
    model_config = ConfigDict(protected_namespaces=()))
    """
    """
    Request model for text-to-speech.
    Request model for text-to-speech.
    """
    """


    text: str = Field(..., description="Text to convert to speech")
    text: str = Field(..., description="Text to convert to speech")
    voice: Optional[str] = Field("default", description="Voice to use")
    voice: Optional[str] = Field("default", description="Voice to use")
    response_format: str = Field(
    response_format: str = Field(
    "mp3", description="Format of the response (mp3 or wav)"
    "mp3", description="Format of the response (mp3 or wav)"
    )
    )


    class TextToSpeechResponse(BaseModel):
    class TextToSpeechResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=()))
    model_config = ConfigDict(protected_namespaces=()))
    """
    """
    Response model for text-to-speech.
    Response model for text-to-speech.
    """
    """


    audio: str = Field(..., description="Base64-encoded audio data")
    audio: str = Field(..., description="Base64-encoded audio data")




    # Define route handlers
    # Define route handlers
    if FASTAPI_AVAILABLE:
    if FASTAPI_AVAILABLE:


    @router.post("/audio/transcriptions", response_model=SpeechToTextResponse)
    @router.post("/audio/transcriptions", response_model=SpeechToTextResponse)
    async def transcribe_audio(
    async def transcribe_audio(
    file: UploadFile = File(...),
    file: UploadFile = File(...),
    model: Optional[str] = Form(None),
    model: Optional[str] = Form(None),
    language: Optional[str] = Form(None),
    language: Optional[str] = Form(None),
    server_model=None,
    server_model=None,
    ):
    ):
    """
    """
    Transcribe audio to text.
    Transcribe audio to text.


    Args:
    Args:
    file: Audio file
    file: Audio file
    model: Model to use for transcription
    model: Model to use for transcription
    language: Language of the audio
    language: Language of the audio
    server_model: Model instance (injected by dependency)
    server_model: Model instance (injected by dependency)


    Returns:
    Returns:
    Transcribed text
    Transcribed text
    """
    """
    if server_model is None:
    if server_model is None:
    raise HTTPException(status_code=500, detail="Model not loaded")
    raise HTTPException(status_code=500, detail="Model not loaded")


    try:
    try:
    # Read audio file
    # Read audio file
    audio_data = await file.read()
    audio_data = await file.read()


    # Transcribe audio
    # Transcribe audio
    result = await _transcribe_audio(server_model, audio_data, model, language)
    result = await _transcribe_audio(server_model, audio_data, model, language)
    return result
    return result


except Exception as e:
except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))
    raise HTTPException(status_code=500, detail=str(e))


    @router.post("/audio/speech", response_model=TextToSpeechResponse)
    @router.post("/audio/speech", response_model=TextToSpeechResponse)
    async def text_to_speech(request: TextToSpeechRequest, model=None):
    async def text_to_speech(request: TextToSpeechRequest, model=None):
    """
    """
    Convert text to speech.
    Convert text to speech.


    Args:
    Args:
    request: Text-to-speech request
    request: Text-to-speech request
    model: Model instance (injected by dependency)
    model: Model instance (injected by dependency)


    Returns:
    Returns:
    Generated audio
    Generated audio
    """
    """
    if model is None:
    if model is None:
    raise HTTPException(status_code=500, detail="Model not loaded")
    raise HTTPException(status_code=500, detail="Model not loaded")


    try:
    try:
    # Generate speech
    # Generate speech
    result = await _text_to_speech(model, request)
    result = await _text_to_speech(model, request)
    return result
    return result


except Exception as e:
except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))
    raise HTTPException(status_code=500, detail=str(e))


    @router.post("/audio/speech/stream")
    @router.post("/audio/speech/stream")
    async def text_to_speech_stream(request: TextToSpeechRequest, model=None):
    async def text_to_speech_stream(request: TextToSpeechRequest, model=None):
    """
    """
    Convert text to speech and stream the audio.
    Convert text to speech and stream the audio.


    Args:
    Args:
    request: Text-to-speech request
    request: Text-to-speech request
    model: Model instance (injected by dependency)
    model: Model instance (injected by dependency)


    Returns:
    Returns:
    Streaming response with audio data
    Streaming response with audio data
    """
    """
    if model is None:
    if model is None:
    raise HTTPException(status_code=500, detail="Model not loaded")
    raise HTTPException(status_code=500, detail="Model not loaded")


    try:
    try:
    # Generate speech
    # Generate speech
    audio_data, content_type = await _text_to_speech_raw(model, request)
    audio_data, content_type = await _text_to_speech_raw(model, request)


    # Stream audio
    # Stream audio
    return StreamingResponse(iter([audio_data]), media_type=content_type)
    return StreamingResponse(iter([audio_data]), media_type=content_type)


except Exception as e:
except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))
    raise HTTPException(status_code=500, detail=str(e))




    # Helper functions
    # Helper functions
    async def _transcribe_audio(model, audio_data, model_name=None, language=None):
    async def _transcribe_audio(model, audio_data, model_name=None, language=None):
    """
    """
    Transcribe audio to text.
    Transcribe audio to text.


    Args:
    Args:
    model: Model instance
    model: Model instance
    audio_data: Audio data
    audio_data: Audio data
    model_name: Model to use for transcription
    model_name: Model to use for transcription
    language: Language of the audio
    language: Language of the audio


    Returns:
    Returns:
    Transcribed text
    Transcribed text
    """
    """
    # Transcribe audio
    # Transcribe audio
    result = model.transcribe_audio(
    result = model.transcribe_audio(
    audio_data=audio_data, model=model_name, language=language
    audio_data=audio_data, model=model_name, language=language
    )
    )


    # Create response
    # Create response
    return {"text": result["text"]}
    return {"text": result["text"]}




    async def _text_to_speech(model, request):
    async def _text_to_speech(model, request):
    """
    """
    Convert text to speech.
    Convert text to speech.


    Args:
    Args:
    model: Model instance
    model: Model instance
    request: Text-to-speech request
    request: Text-to-speech request


    Returns:
    Returns:
    Generated audio
    Generated audio
    """
    """
    # Generate speech
    # Generate speech
    audio_data, _ = await _text_to_speech_raw(model, request)
    audio_data, _ = await _text_to_speech_raw(model, request)


    # Convert to base64
    # Convert to base64
    audio_b64 = base64.b64encode(audio_data).decode("utf-8")
    audio_b64 = base64.b64encode(audio_data).decode("utf-8")


    # Create response
    # Create response
    return {"audio": audio_b64}
    return {"audio": audio_b64}




    async def _text_to_speech_raw(model, request:
    async def _text_to_speech_raw(model, request:
    """
    """
    Convert text to speech and return raw audio data.
    Convert text to speech and return raw audio data.


    Args:
    Args:
    model: Model instance
    model: Model instance
    request: Text-to-speech request
    request: Text-to-speech request


    Returns:
    Returns:
    Generated audio data and content type
    Generated audio data and content type
    """
    """
    # Generate speech
    # Generate speech
    audio_data = model.text_to_speech(
    audio_data = model.text_to_speech(
    text=request.text, voice=request.voice, format=request.response_format
    text=request.text, voice=request.voice, format=request.response_format




    # Determine content type
    # Determine content type
    content_type = "audio/mpeg" if request.response_format == "mp3" else "audio/wav"
    content_type = "audio/mpeg" if request.response_format == "mp3" else "audio/wav"


    return audio_data, content_type
    return audio_data, content_type