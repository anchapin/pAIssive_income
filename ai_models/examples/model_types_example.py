"""
Example usage of the expanded model types.

This script demonstrates how to use the different model types
(ONNX, Quantized, Vision, Audio) in the AI Models module.
"""


import argparse
import logging
import os
import sys

from ai_models.model_types import (AudioModel, ONNXModel, QuantizedModel,
VisionModel)

# Add the parent directory to the path to import the ai_models module
sys.path.append(
os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
# Set up logging
logging.basicConfig(
level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def test_onnx_model(model_path: str, input_text: str) -> None:
    """
    Test an ONNX model.

    Args:
    model_path: Path to the ONNX model
    input_text: Input text for text generation
    """
    print("\n" + "=" * 80)
    print("Testing ONNX Model")
    print("=" * 80)

    try:
    # Create ONNX model
    model = ONNXModel(model_path=model_path, model_type="text-generation")

    # Load the model
    model.load()

    # Get metadata
    metadata = model.get_metadata()
    print("Model Metadata:")
    for key, value in metadata.items():
    print(f"  {key}: {value}")

    # Generate text
    if hasattr(model, "tokenizer") and model.tokenizer:
    print(f"\nGenerating text for prompt: {input_text}")
    output = model.generate_text(input_text)
    print(f"Output: {output}")
    else:
    print("\nTokenizer not available. Cannot generate text.")

except Exception as e:
    print(f"Error testing ONNX model: {e}")


    def test_quantized_model(model_path: str, input_text: str) -> None:
    """
    Test a quantized model.

    Args:
    model_path: Path to the quantized model
    input_text: Input text for text generation
    """
    print("\n" + "=" * 80)
    print("Testing Quantized Model")
    print("=" * 80)

    try:
    # Create quantized model
    model = QuantizedModel(
    model_path=model_path, model_type="text-generation", quantization="4bit"
    )

    # Load the model
    model.load()

    # Get metadata
    metadata = model.get_metadata()
    print("Model Metadata:")
    for key, value in metadata.items():
    print(f"  {key}: {value}")

    # Generate text
    print(f"\nGenerating text for prompt: {input_text}")
    output = model.generate_text(input_text)
    print(f"Output: {output}")

except Exception as e:
    print(f"Error testing quantized model: {e}")


    def test_vision_model(model_path: str, image_path: str) -> None:
    """
    Test a vision model.

    Args:
    model_path: Path to the vision model
    image_path: Path to an image file
    """
    print("\n" + "=" * 80)
    print("Testing Vision Model")
    print("=" * 80)

    try:
    # Create vision model
    model = VisionModel(model_path=model_path, model_type="image-classification")

    # Load the model
    model.load()

    # Get metadata
    metadata = model.get_metadata()
    print("Model Metadata:")
    for key, value in metadata.items():
    print(f"  {key}: {value}")

    # Classify image
    if os.path.exists(image_path):
    print(f"\nClassifying image: {image_path}")
    results = model.classify_image(image_path)

    # Print top 5 results
    print("Top 5 results:")
    for label, score in sorted(
    results.items(), key=lambda x: x[1], reverse=True
    )[:5]:
    print(f"  {label}: {score:.4f}")
    else:
    print(f"\nImage file not found: {image_path}")

except Exception as e:
    print(f"Error testing vision model: {e}")


    def test_audio_model(
    model_path: str, audio_path: str, output_path: str, text: str
    ) -> None:
    """
    Test an audio model.

    Args:
    model_path: Path to the audio model
    audio_path: Path to an audio file
    output_path: Path to save synthesized speech
    text: Text to synthesize
    """
    print("\n" + "=" * 80)
    print("Testing Audio Model")
    print("=" * 80)

    try:
    # Test speech recognition
    if os.path.exists(audio_path):
    print("\nTesting Speech Recognition:")

    # Create audio model for speech recognition
    model = AudioModel(model_path=model_path, model_type="speech-recognition")

    # Load the model
    model.load()

    # Get metadata
    metadata = model.get_metadata()
    print("Model Metadata:")
    for key, value in metadata.items():
    print(f"  {key}: {value}")

    # Transcribe audio
    print(f"\nTranscribing audio: {audio_path}")
    result = model.transcribe(audio_path)
    print(f"Transcription: {result['text']}")
    else:
    print(f"\nAudio file not found: {audio_path}")

    # Test text-to-speech
    print("\nTesting Text-to-Speech:")

    # Create audio model for text-to-speech
    model = AudioModel(model_path=model_path, model_type="text-to-speech")

    # Load the model
    model.load()

    # Get available voices
    try:
    voices = model.get_available_voices()
    if voices:
    print(f"Available voices: {len(voices)}")
    for voice in voices[:5]:  # Show only first 5 voices
    print(f"  {voice['id']}: {voice['name']}")

    # Use the first voice
    voice_id = voices[0]["id"]
    else:
    voice_id = None
    print("No voices available")
except Exception as e:
    voice_id = None
    print(f"Error getting voices: {e}")

    # Synthesize speech
    print(f"\nSynthesizing speech for text: {text}")
    try:
    result = model.synthesize_speech(
    text=text, output_path=output_path, voice_id=voice_id
    )
    print(f"Speech synthesized and saved to: {result['output_path']}")
    print(f"Duration: {result['duration']:.2f} seconds")
except Exception as e:
    print(f"Error synthesizing speech: {e}")

    # Test audio classification
    if os.path.exists(audio_path):
    print("\nTesting Audio Classification:")

    # Create audio model for audio classification
    model = AudioModel(model_path=model_path, model_type="audio-classification")

    # Load the model
    model.load()

    # Classify audio
    print(f"\nClassifying audio: {audio_path}")
    try:
    results = model.classify_audio(audio_path)

    # Print top 5 results
    print("Top 5 results:")
    for label, score in sorted(
    results.items(), key=lambda x: x[1], reverse=True
    )[:5]:
    print(f"  {label}: {score:.4f}")
except Exception as e:
    print(f"Error classifying audio: {e}")

    # Detect sound events
    print("\nDetecting sound events:")
    try:
    events = model.detect_sound_events(audio_path, threshold=0.5)

    print(f"Detected {len(events)} events:")
    for event in events[:5]:  # Show only first 5 events
    print(
    f"  {event['label']} ({event['score']:.4f}) at {event['start_time']:.2f}-{event['end_time']:.2f}s"
    )
except Exception as e:
    print(f"Error detecting sound events: {e}")

except Exception as e:
    print(f"Error testing audio model: {e}")


    def main():
    """
    Main function to demonstrate the expanded model types.
    """
    parser = argparse.ArgumentParser(description="Test different model types")
    parser.add_argument(
    "--model-type",
    type=str,
    choices=["onnx", "quantized", "vision", "audio"],
    help="Type of model to test",
    )
    parser.add_argument("--model-path", type=str, help="Path to the model")
    parser.add_argument(
    "--input-text",
    type=str,
    default="Hello, world!",
    help="Input text for text generation",
    )
    parser.add_argument(
    "--image-path", type=str, help="Path to an image file for vision models"
    )
    parser.add_argument(
    "--audio-path", type=str, help="Path to an audio file for audio models"
    )
    parser.add_argument(
    "--output-path",
    type=str,
    default="output.wav",
    help="Path to save synthesized speech",
    )

    args = parser.parse_args()

    # If no model type is specified, show help
    if not args.model_type:
    parser.print_help()
    return # Check if model path is provided
    if not args.model_path:
    print("Error: --model-path is required")
    return # Test the specified model type
    if args.model_type == "onnx":
    test_onnx_model(args.model_path, args.input_text)
    elif args.model_type == "quantized":
    test_quantized_model(args.model_path, args.input_text)
    elif args.model_type == "vision":
    if not args.image_path:
    print("Error: --image-path is required for vision models")
    return test_vision_model(args.model_path, args.image_path)
    elif args.model_type == "audio":
    if not args.audio_path:
    print("Error: --audio-path is required for audio models")
    return test_audio_model(
    args.model_path, args.audio_path, args.output_path, args.input_text
    )


    if __name__ == "__main__":
    main()